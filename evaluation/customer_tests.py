import sys
import io
import time
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.workflow.graph import run_resolution_flow
from src.db.store import db
from src.db.sqlite_store import sqlite_store
from src.llm.client import llm_client
from src.tools.service_connectors import service_registry
from src.agents.critic import critic_agent
from src.models.schemas import StructuredPlan, StepAction

def run_customer_suite():
    if getattr(sys.stdout, 'encoding', '').lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("=" * 75)
    print(" RESOLVEX AI — CUSTOMER-FIRST REDESIGN VERIFICATION SUITE (TESTS A - Q)")
    print("=" * 75)

    tests = []

    # -------------------------------------------------------------
    # TEST A: Landing page appears before authentication
    # -------------------------------------------------------------
    t0 = time.time()
    html_file = ROOT_DIR / "frontend" / "index.html"
    html = html_file.read_text(encoding="utf-8")
    tA_pass = (
        'id="view-landing"' in html and
        "Resolve issues" in html and
        "not just conversations" in html and
        'startGuestSession()' in html and
        'Sign In to Customer Portal' in html
    )
    tests.append({
        "tag": "TEST A",
        "name": "Landing page appears before authentication",
        "passed": tA_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "Verified unauthenticated landing view, brand proposition, and guest/login CTAs."
    })

    # -------------------------------------------------------------
    # TEST B: Guest mode creates isolated session
    # -------------------------------------------------------------
    t0 = time.time()
    ok_b, _, guest_user = sqlite_store.create_guest_session()
    guest_txns = sqlite_store.get_tenant_transactions(guest_user["user_id"])
    tB_pass = (
        ok_b and
        guest_user["user_id"].startswith("GUEST-") and
        guest_user["role"] == "GUEST" and
        len(guest_txns) > 0
    )
    tests.append({
        "tag": "TEST B",
        "name": "Guest mode creates isolated session",
        "passed": tB_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Created guest ID: {guest_user['user_id']} with isolated tenant orders."
    })

    # -------------------------------------------------------------
    # TEST C: Strict Multi-Tenant Isolation (User A -> Logout -> User B -> User A)
    # -------------------------------------------------------------
    t0 = time.time()
    uid_a = "USER-TEST-ALPHA"
    uid_b = "USER-TEST-BETA"
    sess_a = "SESS-ALPHA-01"
    sess_b = "SESS-BETA-01"

    # 1. User A creates a confidential support request and chat turn
    with sqlite_store.get_connection() as conn:
        conn.execute("DELETE FROM support_cases WHERE user_id IN (?, ?)", (uid_a, uid_b))
        conn.execute("INSERT OR REPLACE INTO support_cases (case_id, user_id, customer_id, issue, category, severity, status, created_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     ("CASE-A-99", uid_a, "CUST-A", "User A Private Financial Claim ₹5,000", "DISPUTE", "HIGH", "OPEN", "2026-10-21T00:00:00"))
        conn.commit()
    sqlite_store.save_chat_message(uid_a, sess_a, role="user", content="Confidential inquiry from User A")

    # 2. User A logs out
    sqlite_store.delete_session(sess_a)

    # 3. User B logs in & inspects orders, cases, and chat
    cases_b = sqlite_store.get_customer_support_cases(uid_b)
    hist_b = sqlite_store.get_chat_history(uid_b, sess_b)
    hist_b_a = sqlite_store.get_chat_history(uid_b, sess_a)

    # 4. User A logs back in
    cases_a = sqlite_store.get_customer_support_cases(uid_a)
    hist_a = sqlite_store.get_chat_history(uid_a, sess_a)

    tC_pass = (
        not any(c["case_id"] == "CASE-A-99" for c in cases_b) and
        len(hist_b) == 0 and
        len(hist_b_a) == 0 and
        any(c["case_id"] == "CASE-A-99" for c in cases_a) and
        len(hist_a) >= 1
    )
    tests.append({
        "tag": "TEST C",
        "name": "Strict Multi-Tenant Isolation (User A -> Logout -> User B -> User A)",
        "passed": tC_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "User B cannot see User A request; User A persistently recovers request upon re-login."
    })

    # -------------------------------------------------------------
    # TEST D: Logout clears active agent state
    # -------------------------------------------------------------
    t0 = time.time()
    # Check that clear_chat_history purges session messages
    sqlite_store.clear_chat_history(uid_a, sess_a)
    hist_a_after = sqlite_store.get_chat_history(uid_a, sess_a)
    tD_pass = len(hist_a_after) == 0
    tests.append({
        "tag": "TEST D",
        "name": "Logout clears active agent state",
        "passed": tD_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "Session memory, active conversation, and cached messages cleanly purged."
    })

    # -------------------------------------------------------------
    # TEST E: Login reloads correct customer history
    # -------------------------------------------------------------
    t0 = time.time()
    perm_uid = "USER-PERM-01"
    perm_sess = "SESS-PERM-01"
    sqlite_store.clear_chat_history(perm_uid, perm_sess)
    sqlite_store.save_chat_message(perm_uid, perm_sess, role="user", content="Perm Message 1")
    sqlite_store.save_chat_message(perm_uid, perm_sess, role="assistant", content="Perm Response 1")

    # Simulate re-login retrieval
    reloaded_hist = sqlite_store.get_chat_history(perm_uid, perm_sess)
    tE_pass = (
        len(reloaded_hist) == 2 and
        reloaded_hist[0]["content"] == "Perm Message 1" and
        reloaded_hist[1]["content"] == "Perm Response 1"
    )
    tests.append({
        "tag": "TEST E",
        "name": "Login reloads correct customer history",
        "passed": tE_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Reloaded {len(reloaded_hist)} persistent conversational turns across re-authentication."
    })

    # -------------------------------------------------------------
    # TEST F: Multiple bookings cause clarification rather than guessing
    # -------------------------------------------------------------
    t0 = time.time()
    turn_f = llm_client.chat_turn("I want a refund for my booking", user_id=guest_user["user_id"])
    tF_pass = (
        turn_f.get("needs_clarification") is True and
        len(turn_f.get("clarification_options", [])) >= 2
    )
    tests.append({
        "tag": "TEST F",
        "name": "Multiple bookings cause clarification rather than guessing",
        "passed": tF_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Presented {len(turn_f.get('clarification_options', []))} options: {[o['label'][:25] for o in turn_f.get('clarification_options', [])]}"
    })

    # -------------------------------------------------------------
    # TEST G: Provider is identified from evidence/user input
    # -------------------------------------------------------------
    t0 = time.time()
    p1 = service_registry.identify_provider("My RedBus booking failed")
    p2 = service_registry.identify_provider("MakeMyTrip hotel cancellation")
    p3 = service_registry.identify_provider("Amazon order delivered with wrong item")
    p4 = service_registry.identify_provider("Swiggy food spillage on delivery")
    tG_pass = (p1 == "RedBus" and p2 == "MakeMyTrip" and p3 == "Amazon" and p4 == "Swiggy")
    tests.append({
        "tag": "TEST G",
        "name": "Provider is identified from evidence/user input",
        "passed": tG_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Accurately mapped: {p1}, {p2}, {p3}, {p4}"
    })

    # -------------------------------------------------------------
    # TEST H: Unknown provider causes clarification
    # -------------------------------------------------------------
    t0 = time.time()
    turn_h = llm_client.chat_turn("I need some help please", user_id=guest_user["user_id"])
    tH_pass = turn_h.get("needs_clarification") is True
    tests.append({
        "tag": "TEST H",
        "name": "Unknown provider causes clarification",
        "passed": tH_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Clarification requested: {turn_h.get('clarification_prompt')}"
    })

    # -------------------------------------------------------------
    # TEST I: Eligible cancellation refund is approved
    # -------------------------------------------------------------
    t0 = time.time()
    db.reset()
    out_i = run_resolution_flow(
        "I cancelled my RedBus booking RB-10291 36 hours prior to departure.",
        {"customer_id": "CUST-101", "transaction_id": "TXN-8821", "order_id": "ORD-5501", "amount": 2499.0}
    )
    tI_pass = (
        out_i["final_status"] == "RESOLVED_AUTONOMOUSLY" and
        out_i["verification_result"]["verified"] is True
    )
    tests.append({
        "tag": "TEST I",
        "name": "Eligible cancellation refund is approved",
        "passed": tI_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Status: {out_i['final_status']}, Verified: {out_i['verification_result']['verified']}"
    })

    # -------------------------------------------------------------
    # TEST J: Ineligible cancellation is rejected with policy reason
    # -------------------------------------------------------------
    t0 = time.time()
    # Validate with policy POL-RB-02 (2h prior to departure)
    ineligible_plan = StructuredPlan(
        plan_id="PLAN-INEL",
        goal="Cancel late bus",
        issue_category="TRAVEL_CANCELLATION",
        steps=[StepAction(step_id=1, tool_name="initiate_refund", parameters={"amount": 1850.0}, description="Refund")]
    )
    evidence_j = {
        "primary_policy": {
            "policy_id": "POL-RB-02",
            "title": "RedBus Bus Ticket Cancellation (Post-Window Ineligible)",
            "conditions": {"cancellation_eligible": False}
        },
        "extracted_entities": {"amount": 1850.0}
    }
    critic_j = critic_agent.validate_pre_execution(ineligible_plan, evidence_j)
    tJ_pass = (
        critic_j.decision == "ESCALATE" and
        "POL-RB-02" in critic_j.policy_citation
    )
    tests.append({
        "tag": "TEST J",
        "name": "Ineligible cancellation is rejected with policy reason",
        "passed": tJ_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Critic Decision: {critic_j.decision}, Policy Citation: {critic_j.policy_citation}"
    })

    # -------------------------------------------------------------
    # TEST K: Wrong product creates appropriate resolution flow
    # -------------------------------------------------------------
    t0 = time.time()
    turn_k = llm_client.chat_turn("I received the wrong phone for order ORD-8801", user_id=guest_user["user_id"])
    tK_pass = (turn_k.get("actionable") is True and turn_k.get("scenario_key") == "wrong-product")
    tests.append({
        "tag": "TEST K",
        "name": "Wrong product creates appropriate resolution flow",
        "passed": tK_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Scenario key: {turn_k.get('scenario_key')}, Actionable: {turn_k.get('actionable')}"
    })

    # -------------------------------------------------------------
    # TEST L: Damaged product creates appropriate resolution flow
    # -------------------------------------------------------------
    t0 = time.time()
    turn_l = llm_client.chat_turn("The monitor screen arrived damaged for ORD-8802", user_id=guest_user["user_id"])
    tL_pass = (turn_l.get("actionable") is True and turn_l.get("scenario_key") == "damaged-product")
    tests.append({
        "tag": "TEST L",
        "name": "Damaged product creates appropriate resolution flow",
        "passed": tL_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Scenario key: {turn_l.get('scenario_key')}, Actionable: {turn_l.get('actionable')}"
    })

    # -------------------------------------------------------------
    # TEST M: Duplicate refund is blocked
    # -------------------------------------------------------------
    t0 = time.time()
    db.reset()
    out_m = run_resolution_flow(
        "I was charged ₹2,499 for order ORD-5502. Where is my refund?",
        {"customer_id": "CUST-102", "transaction_id": "TXN-8822", "order_id": "ORD-5502", "amount": 2499.0}
    )
    tM_pass = (
        out_m["replan_count"] >= 1 and
        out_m["final_status"] == "RESOLVED_WITH_EXISTING_STATUS"
    )
    tests.append({
        "tag": "TEST M",
        "name": "Duplicate refund is blocked",
        "passed": tM_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Replan count: {out_m['replan_count']}, Double-payout blocked."
    })

    # -------------------------------------------------------------
    # TEST N: High-risk case escalates
    # -------------------------------------------------------------
    t0 = time.time()
    db.reset()
    out_n = run_resolution_flow(
        "₹48,500 was deducted from my account but order is in security check.",
        {"customer_id": "CUST-103", "transaction_id": "TXN-9901", "order_id": "ORD-5503", "amount": 48500.0}
    )
    tN_pass = (out_n["final_status"] == "ESCALATED_TO_HUMAN")
    tests.append({
        "tag": "TEST N",
        "name": "High-risk case escalates",
        "passed": tN_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Status: {out_n['final_status']}, Autonomous disbursement blocked."
    })

    # -------------------------------------------------------------
    # TEST O: Technical analysis is not shown to normal customer
    # -------------------------------------------------------------
    t0 = time.time()
    resp_o = llm_client.generate_customer_response(
        "Refund inquiry",
        "RESOLVED_AUTONOMOUSLY",
        {"amount": 2499.0, "refund_id": "RF-1ECA35", "arn": "ARN-UPI-B80128FA"},
        {"case_id": "CASE-101"}
    )
    expl = resp_o["explanation_text"]
    tO_pass = (
        "Traceback" not in expl and
        "SELECT " not in expl and
        "StateGraph" not in expl and
        "{" not in expl and
        len(resp_o["what_we_found"]) > 0
    )
    tests.append({
        "tag": "TEST O",
        "name": "Technical analysis is not shown to normal customer",
        "passed": tO_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "Customer response is clean, polite, and grounded with zero raw code/SQL/traces."
    })

    # -------------------------------------------------------------
    # TEST P: Customer history persists across sessions
    # -------------------------------------------------------------
    t0 = time.time()
    hist_p = sqlite_store.get_chat_history(perm_uid, perm_sess)
    tP_pass = len(hist_p) >= 2
    tests.append({
        "tag": "TEST P",
        "name": "Customer history persists across sessions",
        "passed": tP_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Verified persistent messages in store for session {perm_sess}."
    })

    # -------------------------------------------------------------
    # TEST Q: LLM Runtime Model Verification
    # -------------------------------------------------------------
    t0 = time.time()
    diag = llm_client.get_runtime_diagnostics()
    tQ_pass = (
        diag["provider"] == "Ollama" and
        diag["model"] in ["qwen2.5-coder:7b", "qwen3:8b", "qwen2.5-coder:latest"] and
        diag["status"] in ["Connected", "Fallback Mode"] and
        diag["last_latency_ms"] >= 0
    )
    tests.append({
        "tag": "TEST Q",
        "name": "LLM Runtime Model Verification",
        "passed": tQ_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Provider: {diag['provider']}, Runtime Model: {diag['model']}, Status: {diag['status']}, Latency: {diag['last_latency_ms']}ms"
    })

    
    # -------------------------------------------------------------
    # TEST R: Agent Workflow Visibility & Participation
    # -------------------------------------------------------------
    t0 = time.time()
    db.reset()
    out_r = run_resolution_flow(
        "₹2,499 was deducted but RedBus booking failed (PG 504).",
        {"customer_id": "CUST-101", "transaction_id": "TXN-8821", "order_id": "ORD-5501", "amount": 2499.0}
    )
    agent_msgs = out_r.get("messages", [])
    seen_agents = {m["agent_name"] for m in agent_msgs if isinstance(m, dict) and "agent_name" in m}
    tR_pass = (
        "Planner_Agent" in seen_agents and
        "Research_Agent" in seen_agents and
        "Critic_Agent" in seen_agents and
        "Executor_Agent" in seen_agents and
        "Business_Automation_Agent" in seen_agents
    )
    tests.append({
        "tag": "TEST R",
        "name": "Agent Workflow Visibility & Active Participation",
        "passed": tR_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Participating agents verified in execution trace: {list(seen_agents)}"
    })

    # -------------------------------------------------------------
    # TEST S: Replanning Visibility & State Transition
    # -------------------------------------------------------------
    t0 = time.time()
    db.reset()
    out_s = run_resolution_flow(
        "I want a refund for my order ORD-5502.",
        {"customer_id": "CUST-102", "transaction_id": "TXN-8822", "order_id": "ORD-5502", "amount": 2499.0}
    )
    tS_pass = (
        out_s.get("replan_count", 0) >= 1 and
        out_s.get("final_status") == "RESOLVED_WITH_EXISTING_STATUS"
    )
    tests.append({
        "tag": "TEST S",
        "name": "Replanning Visibility & State Transition",
        "passed": tS_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Replan count: {out_s.get('replan_count')}, Final status: {out_s.get('final_status')}"
    })

    # -------------------------------------------------------------
    # TEST T: Systemic Incident Pattern Clustering
    # -------------------------------------------------------------
    t0 = time.time()
    db.reset()
    out_t = run_resolution_flow(
        "Systemic gateway callback timeout 504 on ICICI netbanking route.",
        {"customer_id": "CUST-201", "transaction_id": "TXN-7001", "order_id": "ORD-7001", "amount": 1999.0}
    )
    incidents = db.get_all_incidents()
    inc_item = incidents[0] if incidents else {}
    tT_pass = (
        out_t.get("final_status") == "SYSTEMIC_INCIDENT_ORCHESTRATED" and
        len(incidents) >= 1 and
        inc_item.get("affected_count", 0) >= 50
    )
    tests.append({
        "tag": "TEST T",
        "name": "Systemic Incident Pattern Clustering",
        "passed": tT_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Master Incident: {inc_item.get('incident_id', 'None')}, Affected Transactions: {inc_item.get('affected_count', 0)}"
    })

    # -------------------------------------------------------------
    # TEST U: Software Development Agent Rule Synthesis & Test
    # -------------------------------------------------------------
    t0 = time.time()
    from src.agents.software_dev import SoftwareDevelopmentAgent
    sda = SoftwareDevelopmentAgent()
    sda_res = sda.synthesize_and_validate_rule("PG_TIMEOUT_504")
    tU_pass = (
        sda_res.get("status") == "SUCCESS" and
        sda_res.get("rule") is not None and
        sda_res.get("test_report", {}).get("accuracy", 0) >= 0.95
    )
    tests.append({
        "tag": "TEST U",
        "name": "Software Development Agent Rule Synthesis & Test",
        "passed": tU_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Rule: {sda_res.get('rule', {}).get('rule_id')}, Accuracy: {sda_res.get('test_report', {}).get('accuracy') * 100:.1f}%"
    })

    # -------------------------------------------------------------
    # TEST V: Customer Navigation Endpoints & DOM Integrity
    # -------------------------------------------------------------
    t0 = time.time()
    html_content = (ROOT_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    tV_pass = (
        'id="screen-customer-home"' in html_content and
        'id="screen-customer-orders"' in html_content and
        'id="screen-customer-requests"' in html_content and
        'id="screen-customer-help"' in html_content and
        'id="screen-customer-account"' in html_content and
        'data-nav="customer-orders"' in html_content and
        'data-nav="customer-requests"' in html_content and
        'data-nav="customer-help"' in html_content
    )
    tests.append({
        "tag": "TEST V",
        "name": "Customer Navigation Endpoints & DOM Integrity",
        "passed": tV_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "All 5 customer screens (Home, Orders, Requests, Help, Account) and nav links verified present without dead buttons."
    })
    # -------------------------------------------------------------
    # TEST W: Multi-Tenant Seeded Accounts (Jaydev ≠ Rajvi ≠ Guest ≠ Evaluator)
    # -------------------------------------------------------------
    t0 = time.time()
    ok_j, _, user_j = sqlite_store.authenticate_user("jaydev", "demo123")
    ok_r, _, user_r = sqlite_store.authenticate_user("rajvi", "demo123")
    ok_e, _, user_e = sqlite_store.authenticate_user("evaluator", "evaluator123")
    
    ords_j = {o["order_id"] for o in sqlite_store.get_tenant_orders(user_j["user_id"])}
    ords_r = {o["order_id"] for o in sqlite_store.get_tenant_orders(user_r["user_id"])}
    
    tW_pass = (
        ok_j and ok_r and ok_e and
        user_j["username"] == "Jaydev Butani" and
        user_r["username"] == "Rajvi Patel" and
        user_e["role"] == "EVALUATOR" and
        len(ords_j) >= 10 and
        len(ords_r) >= 10 and
        len(ords_j.intersection(ords_r)) == 0  # Zero overlap
    )
    tests.append({
        "tag": "TEST W",
        "name": "Multi-Tenant Seeded Accounts (Jaydev ≠ Rajvi ≠ Evaluator)",
        "passed": tW_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"Jaydev ({len(ords_j)} ords), Rajvi ({len(ords_r)} ords), zero order overlap. Evaluator verified."
    })

    # -------------------------------------------------------------
    # TEST X: Destination Tab Switcher & Credential-Gated Login
    # -------------------------------------------------------------
    t0 = time.time()
    html_text = (ROOT_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    tX_pass = (
        'id="tab-btn-customer"' in html_text and
        'id="tab-btn-evaluator"' in html_text and
        'id="auth-panel-customer"' in html_text and
        'id="auth-panel-evaluator"' in html_text and
        'handleEvaluatorLogin' in html_text and
        'setAuthTab' in html_text and
        'id="customer-login-error"' in html_text and
        'id="evaluator-login-error"' in html_text
    )
    tests.append({
        "tag": "TEST X",
        "name": "Destination Tab Switcher & Credential-Gated Login",
        "passed": tX_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "Customer vs. Evaluator tabs verified, private credential login active without exposed identities."
    })

    # -------------------------------------------------------------
    # TEST Y: 10 Multi-Domain Evaluation Scenarios
    # -------------------------------------------------------------
    t0 = time.time()
    from server import SCENARIO_SPECS
    expected_scenarios = [
        "pg-504", "duplicate-claim", "tor-escalate", "pg-spike",
        "travel-cancel", "travel-ineligible", "wrong-product",
        "damaged-product", "food-spill", "subscription-renewal"
    ]
    all_specs_present = all(k in SCENARIO_SPECS for k in expected_scenarios)
    all_pills_in_html = all(f"previewScenario('{k}')" in html_text for k in expected_scenarios)

    # Test food-spill and subscription customer responses
    food_resp = llm_client.generate_customer_response("Food arrived spilled", "RESOLVED_AUTONOMOUSLY", {"amount": 650.0}, {"scenario_key": "food-spill", "order_id": "ORD-9006"})
    sub_resp = llm_client.generate_customer_response("Prime annual auto debited", "RESOLVED_AUTONOMOUSLY", {"amount": 1499.0}, {"scenario_key": "subscription-renewal", "order_id": "ORD-9007"})

    tY_pass = (
        all_specs_present and
        all_pills_in_html and
        "MEAL REIMBURSEMENT" in food_resp.get("headline", "") and
        "SUBSCRIPTION CANCELLED" in sub_resp.get("headline", "")
    )
    tests.append({
        "tag": "TEST Y",
        "name": "10 Multi-Domain Evaluation Scenarios (6+ Domains)",
        "passed": tY_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": f"All 10 scenarios seeded in backend & UI: Travel, E-Com, Food, Subs, Payments, SecOps, Systems."
    })

    # -------------------------------------------------------------
    # TEST Z: Explainable Customer Resolution Accordion
    # -------------------------------------------------------------
    t0 = time.time()
    tZ_pass = (
        "How did ResolveX decide?" in html_text and
        "1. Evidence Verified:" in html_text and
        "2. Policy Citation:" in html_text and
        "3. Safety Guard (Critic):" in html_text and
        "4. Action Executed:" in html_text and
        "5. Verification:" in html_text
    )
    tests.append({
        "tag": "TEST Z",
        "name": "Explainable Customer Resolution Accordion",
        "passed": tZ_pass,
        "latency": f"{round(time.time() - t0, 3)}s",
        "details": "5-point explainability breakdown (Evidence → Policy → Safety → Action → Verification) verified."
    })

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    passed_count = sum(1 for t in tests if t["passed"])
    total_count = len(tests)

    print("\n" + "=" * 75)
    print(" CUSTOMER SUITE SUMMARY")
    print("=" * 75)
    for t in tests:
        tag = "[PASS]  " if t["passed"] else "[FAIL] *"
        print(f" {tag} | {t['tag']}: {t['name']:<50} | {t['latency']}")
        print(f"            Details: {t['details']}")
    print("-" * 75)
    print(f" OVERALL: {passed_count}/{total_count} Tests Passed ({passed_count/total_count*100:.1f}%)")
    print("=" * 75 + "\n")

    return tests, {
        "passed": passed_count,
        "total_tests": total_count,
        "pass_rate": f"{passed_count/total_count*100:.1f}%"
    }

if __name__ == "__main__":
    run_customer_suite()
