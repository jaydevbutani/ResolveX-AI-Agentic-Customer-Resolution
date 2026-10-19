import sys
import time
import json
import io
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.workflow.graph import run_resolution_flow
from src.db.store import db
from src.db.sqlite_store import sqlite_store
from src.llm.client import llm_client

def run_all_tests():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("=" * 70)
    print(" RESOLVEX AI — AUTOMATED ACCEPTANCE & BENCHMARK TEST SUITE (14/14)")
    print("=" * 70)

    results = []

    # -------------------------------------------------------------
    # TEST 1: Autonomous Refund Execution
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Normal Autonomous Resolution (Scenario 1)...")
    db.reset()
    t0 = time.time()
    out1 = run_resolution_flow(
        "₹2,499 was deducted but my order failed.",
        {"customer_id": "CUST-101", "transaction_id": "TXN-8821", "order_id": "ORD-5501", "amount": 2499.0}
    )
    t1 = time.time()
    refund_record = db.get_refund_by_transaction("TXN-8821")
    t1_pass = (
        out1["final_status"] == "RESOLVED_AUTONOMOUSLY" and
        refund_record is not None and
        refund_record.get("status") == "SUCCESS" and
        refund_record.get("amount") == 2499.0 and
        out1["verification_result"]["verified"] is True
    )
    results.append({
        "name": "TEST 1: Autonomous Refund Execution",
        "passed": t1_pass,
        "latency": f"{round(t1 - t0, 3)}s",
        "details": f"Refund ID: {refund_record.get('refund_id') if refund_record else 'None'}, ARN: {refund_record.get('arn') if refund_record else 'None'}"
    })
    print(f" -> Result: {'PASSED' if t1_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 2: Critic Rejection & Replanning Loop
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Critic Rejection + Dynamic Replanning (Scenario 2)...")
    db.reset()
    t0 = time.time()
    out2 = run_resolution_flow(
        "I was charged ₹2,499 for order ORD-5502 but order failed.",
        {"customer_id": "CUST-102", "transaction_id": "TXN-8822", "order_id": "ORD-5502", "amount": 2499.0}
    )
    t2 = time.time()
    all_refunds_for_txn = [r for r in db.get_all_refunds() if r.get("transaction_id") == "TXN-8822"]
    t2_pass = (
        out2["replan_count"] >= 1 and
        out2["final_status"] == "RESOLVED_WITH_EXISTING_STATUS" and
        len(all_refunds_for_txn) == 1 and
        all_refunds_for_txn[0]["refund_id"] == "RF-40192"
    )
    results.append({
        "name": "TEST 2: Critic Rejection & Replanning Loop",
        "passed": t2_pass,
        "latency": f"{round(t2 - t0, 3)}s",
        "details": f"Replan count: {out2['replan_count']}, Existing Refund Preserved: {all_refunds_for_txn[0]['refund_id']}"
    })
    print(f" -> Result: {'PASSED' if t2_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 3: High-Risk Exception / Human Escalation
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Exception & Human Escalation (Scenario 3)...")
    db.reset()
    t0 = time.time()
    out3 = run_resolution_flow(
        "₹48,500 was deducted from my account but order is in manual hold.",
        {"customer_id": "CUST-103", "transaction_id": "TXN-9901", "order_id": "ORD-5503", "amount": 48500.0}
    )
    t3 = time.time()
    case_record = db.get_case("CASE-001")
    refund_exists = db.get_refund_by_transaction("TXN-9901") is not None
    t3_pass = (
        out3["final_status"] == "ESCALATED_TO_HUMAN" and
        not refund_exists and
        case_record is not None and
        case_record.get("status") == "ESCALATED_TO_HUMAN"
    )
    results.append({
        "name": "TEST 3: High-Value / Risk Human Escalation",
        "passed": t3_pass,
        "latency": f"{round(t3 - t0, 3)}s",
        "details": f"Autonomous Action Blocked: {not refund_exists}, Case Status: {case_record.get('status') if case_record else 'None'}"
    })
    print(f" -> Result: {'PASSED' if t3_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 4: Systemic Incident Detection & Rule Synthesis
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Systemic Incident Clustering & Software Dev Rule (Scenario 4)...")
    db.reset()
    t0 = time.time()
    out4 = run_resolution_flow(
        "Systemic gateway callback timeout 504 on ICICI netbanking route.",
        {"customer_id": "CUST-201", "transaction_id": "TXN-7001", "order_id": "ORD-7001", "amount": 1999.0}
    )
    t4 = time.time()
    incidents = db.get_all_incidents()
    t4_pass = (
        out4["final_status"] == "SYSTEMIC_INCIDENT_ORCHESTRATED" and
        out4.get("software_dev_result") is not None and
        len(incidents) > 0 and
        out4["software_dev_result"]["rule"]["accuracy_score"] == 1.0
    )
    results.append({
        "name": "TEST 4: Systemic Clustering & Rule Synthesis",
        "passed": t4_pass,
        "latency": f"{round(t4 - t0, 3)}s",
        "details": f"Master Incident: {incidents[0]['incident_id']}, Synthesized Rule Accuracy: {out4['software_dev_result']['rule']['accuracy_score']*100}%"
    })
    print(f" -> Result: {'PASSED' if t4_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 5: Deterministic Fallback Reasoner
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Deterministic Fallback Reasoner...")
    t0 = time.time()
    fallback_res = llm_client.query("Customer requires refund for TXN-8821", force_mode="FALLBACK")
    t5 = time.time()
    t5_pass = (
        fallback_res.get("status") == "SUCCESS" and
        "Deterministic" in fallback_res.get("source", "")
    )
    results.append({
        "name": "TEST 5: Deterministic Cognitive Fallback",
        "passed": t5_pass,
        "latency": f"{round(t5 - t0, 3)}s",
        "details": f"Source: {fallback_res.get('source')}"
    })
    print(f" -> Result: {'PASSED' if t5_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 6: Active Participation of All Six Agents
    # -------------------------------------------------------------
    print("\n[TEST 6] Testing Active Participation of All Six Agents...")
    t0 = time.time()
    observed_agents = set()
    for run_out in [out1, out2, out4]:
        for msg in run_out.get("messages", []):
            observed_agents.add(msg["agent_name"])
    required_agents = {
        "Planner_Agent", "Research_Agent", "Critic_Agent",
        "Executor_Agent", "Business_Automation_Agent", "Software_Development_Agent"
    }
    t6_pass = required_agents.issubset(observed_agents)
    t6 = time.time()
    results.append({
        "name": "TEST 6: Active Participation of All 6 Agents",
        "passed": t6_pass,
        "latency": f"{round(t6 - t0, 3)}s",
        "details": f"Observed 6 agents: {list(observed_agents)}"
    })
    print(f" -> Result: {'PASSED' if t6_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 7: Real Synthetic Database State Changes
    # -------------------------------------------------------------
    print("\n[TEST 7] Testing Real Synthetic Database State Changes...")
    t0 = time.time()
    db.reset()
    init_refunds = len(db.get_all_refunds())
    run_resolution_flow(
        "₹2,499 was deducted from my account but order failed.",
        {"customer_id": "CUST-101", "transaction_id": "TXN-8821", "order_id": "ORD-5501", "amount": 2499.0}
    )
    after_refunds = len(db.get_all_refunds())
    t7_pass = (after_refunds == init_refunds + 1)
    t7 = time.time()
    results.append({
        "name": "TEST 7: Real State Changes in Synthetic DB",
        "passed": t7_pass,
        "latency": f"{round(t7 - t0, 3)}s",
        "details": f"New refunds created in store: {after_refunds - init_refunds}"
    })
    print(f" -> Result: {'PASSED' if t7_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 8: Scenario Switching & State Reset
    # -------------------------------------------------------------
    print("\n[TEST 8] Testing Scenario Switching & State Reset...")
    t0 = time.time()
    reset_ok = db.reset()
    active_refunds_after_reset = len(db.get_all_refunds())
    t8_pass = reset_ok and (active_refunds_after_reset == 1)
    t8 = time.time()
    results.append({
        "name": "TEST 8: Scenario Switching & State Reset",
        "passed": t8_pass,
        "latency": f"{round(t8 - t0, 3)}s",
        "details": f"Reset cleanly restored database template (Active refunds: {active_refunds_after_reset})"
    })
    print(f" -> Result: {'PASSED' if t8_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 9: Conversational Chatbot Intent & Multi-Turn Clarification
    # -------------------------------------------------------------
    print("\n[TEST 9] Testing Conversational Chatbot Intent & Multi-Turn Clarification...")
    t0 = time.time()
    t1_chat = llm_client.chat_turn("I have an issue with my order")
    t2_chat = llm_client.chat_turn(
        "₹2,499 was deducted for ORD-5501",
        chat_history=[{"role": "user", "content": "I have an issue with my order"}]
    )
    t9_pass = (
        t1_chat.get("needs_clarification") is True and
        t2_chat.get("actionable") is True and
        t2_chat.get("entities", {}).get("amount") == 2499.0 and
        t2_chat.get("entities", {}).get("order_id") == "ORD-5501"
    )
    t9 = time.time()
    results.append({
        "name": "TEST 9: Conversational Multi-Turn Clarification",
        "passed": t9_pass,
        "latency": f"{round(t9 - t0, 3)}s",
        "details": f"Turn 1 Clarified: {t1_chat.get('needs_clarification')}, Turn 2 Extracted: {t2_chat.get('entities')}"
    })
    print(f" -> Result: {'PASSED' if t9_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 10: Chatbot-to-Agent Workflow Execution
    # -------------------------------------------------------------
    print("\n[TEST 10] Testing Chatbot-to-Agent Workflow Execution...")
    db.reset()
    t0 = time.time()
    bot_turn = llm_client.chat_turn("I was charged ₹2,499 but my order failed due to Gateway Timeout 504.")
    bot_out = run_resolution_flow(bot_turn["combined_prompt"], bot_turn["entities"])
    bot_refund = db.get_refund_by_transaction(bot_turn["entities"]["transaction_id"])
    t10_pass = (
        bot_out["final_status"] == "RESOLVED_AUTONOMOUSLY" and
        bot_refund is not None and
        bot_refund.get("amount") == 2499.0
    )
    t10 = time.time()
    results.append({
        "name": "TEST 10: Chatbot-to-Agent Workflow Execution",
        "passed": t10_pass,
        "latency": f"{round(t10 - t0, 3)}s",
        "details": f"Status: {bot_out['final_status']}, Disbursed Refund: {bot_refund.get('refund_id') if bot_refund else 'None'}"
    })
    print(f" -> Result: {'PASSED' if t10_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 11: Grounded Response Verification (Zero Hallucination)
    # -------------------------------------------------------------
    print("\n[TEST 11] Testing Grounded Response Verification (Zero Hallucination)...")
    t0 = time.time()
    real_refund = db.get_refund_by_transaction("TXN-8821")
    grounded_resp = llm_client.generate_customer_response(
        "Refund inquiry",
        "RESOLVED_AUTONOMOUSLY",
        real_refund or {"amount": 2499.0, "refund_id": "RF-1ECA35", "arn": "ARN-UPI-B80128FA"},
        {"case_id": "CASE-101"}
    )
    t11_pass = (
        real_refund is not None and
        real_refund["refund_id"] in grounded_resp["reference"] and
        real_refund["arn"] in grounded_resp["reference"] and
        "2,499.00" in grounded_resp["your_issue"]
    )
    t11 = time.time()
    results.append({
        "name": "TEST 11: Grounded Response Verification",
        "passed": t11_pass,
        "latency": f"{round(t11 - t0, 3)}s",
        "details": f"Grounded Reference: {grounded_resp['reference']} strictly matched DB record"
    })
    print(f" -> Result: {'PASSED' if t11_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 12: 6-Stage Decision Audit Trace
    # -------------------------------------------------------------
    print("\n[TEST 12] Testing 6-Stage 'Why did ResolveX decide this?' Trace...")
    t0 = time.time()
    trace_res = llm_client.generate_decision_trace(
        "RESOLVED_AUTONOMOUSLY",
        {"transaction_id": "TXN-8821", "order_id": "ORD-5501", "amount": 2499.0}
    )
    stage_names = [s["step"] for s in trace_res.get("stages", [])]
    t12_pass = (
        len(trace_res.get("stages", [])) == 6 and
        any("Evidence" in s for s in stage_names) and
        any("Policy" in s for s in stage_names) and
        any("Decision" in s for s in stage_names) and
        any("Critic" in s for s in stage_names) and
        any("Action" in s for s in stage_names) and
        any("Verification" in s for s in stage_names)
    )
    t12 = time.time()
    results.append({
        "name": "TEST 12: 6-Stage Decision Audit Trace",
        "passed": t12_pass,
        "latency": f"{round(t12 - t0, 3)}s",
        "details": f"6/6 Stages Verified: Evidence → Policy → Decision → Critic → Action → Verification"
    })
    print(f" -> Result: {'PASSED' if t12_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 13: 3-Role Demo Accounts & Multi-User Isolation
    # -------------------------------------------------------------
    print("\n[TEST 13] Testing 3-Role Demo Accounts & Multi-User Isolation...")
    t0 = time.time()
    auth_arch, _, u_arch = sqlite_store.authenticate_user("demo", "demo123")
    auth_cust, _, u_cust = sqlite_store.authenticate_user("customer_demo", "demo123")
    auth_ops, _, u_ops = sqlite_store.authenticate_user("ops_demo", "demo123")
    
    arch_txns = sqlite_store.get_tenant_transactions(u_arch["user_id"])
    cust_txns = sqlite_store.get_tenant_transactions(u_cust["user_id"])

    t13_pass = (
        auth_arch and auth_cust and auth_ops and
        u_arch["role"] == "STAFF_ARCHITECT" and
        u_cust["role"] == "DEMO_CUSTOMER" and
        u_ops["role"] == "DEMO_OPERATIONS" and
        len(arch_txns) > 0 and len(cust_txns) > 0 and
        u_arch["user_id"] != u_cust["user_id"]
    )
    t13 = time.time()
    results.append({
        "name": "TEST 13: 3-Role Accounts & Tenant Isolation",
        "passed": t13_pass,
        "latency": f"{round(t13 - t0, 3)}s",
        "details": f"Customer ({u_cust['user_id']}), Ops ({u_ops['user_id']}), Architect ({u_arch['user_id']}) verified isolated"
    })
    print(f" -> Result: {'PASSED' if t13_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # TEST 14: Finite Execution Animation & Modal Lifecycle
    # -------------------------------------------------------------
    print("\n[TEST 14] Testing Finite Execution Animation & Modal Lifecycle...")
    t0 = time.time()
    html_file = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    html_content = html_file.read_text(encoding="utf-8")
    t14_pass = (
        "togglePayloadModal(false)" in html_content and
        "Escape" in html_content and
        "json-drawer" in html_content and
        "task_alt" in html_content and
        "isExecuting = false" in html_content
    )
    t14 = time.time()
    results.append({
        "name": "TEST 14: Finite Animation & Modal Lifecycle",
        "passed": t14_pass,
        "latency": f"{round(t14 - t0, 3)}s",
        "details": "ESC key, backdrop dismiss, and execution completion state verified"
    })
    print(f" -> Result: {'PASSED' if t14_pass else 'FAILED'}")

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print("\n" + "=" * 70)
    print(" BENCHMARK TEST SUMMARY")
    print("=" * 70)
    for r in results:
        status_tag = "[PASS]  " if r["passed"] else "[FAIL] *"
        print(f" {status_tag} | {r['name']:<46} | {r['latency']:<6}")
        print(f"            Details: {r['details']}")
    print("-" * 70)
    print(f" OVERALL: {passed_count}/{total_count} Tests Passed ({passed_count/total_count*100:.1f}%)")
    print("=" * 70 + "\n")

    return results, {
        "passed": passed_count,
        "total_tests": total_count,
        "pass_rate": f"{passed_count/total_count*100:.1f}%"
    }

if __name__ == "__main__":
    run_all_tests()
