import copy
import logging
from datetime import datetime
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from src.workflow.state import AgentState
from src.agents.planner import planner_agent
from src.agents.research import research_agent
from src.agents.critic import critic_agent
from src.agents.executor import executor_agent
from src.agents.business_automation import business_automation_agent
from src.agents.software_dev import software_dev_agent
from src.db.store import db
from src.models.schemas import StepAction, StructuredPlan

logger = logging.getLogger("ResolveX.Workflow")

def _add_message(state: AgentState, agent_name: str, stage: str, message: str, level: str = "INFO", data: Any = None) -> List[Dict[str, Any]]:
    msgs = list(state.get("messages", []))
    msgs.append({
        "agent_name": agent_name,
        "stage": stage,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "data": data
    })
    return msgs

def research_node(state: AgentState) -> Dict[str, Any]:
    text = state["complaint_text"]
    ctx = state["context"]

    # Capture initial database snapshot
    before_snap = db.get_snapshot()

    # Research Agent gathers evidence and grounded policies
    evidence = research_agent.analyze_complaint(text, ctx)
    primary_pol = evidence.get("primary_policy")
    pol_id = primary_pol.get("policy_id", "N/A") if primary_pol else "N/A"

    msgs = _add_message(
        state,
        "Research_Agent",
        "INVESTIGATE",
        f"Retrieved policy {pol_id} via RAG. Context verified for {ctx.get('transaction_id', 'Transaction')}.",
        level="INFO",
        data={"policy_id": pol_id, "customer_id": ctx.get("customer_id")}
    )

    # Check for systemic pattern
    if evidence.get("systemic_pattern"):
        pat = evidence["systemic_pattern"]
        msgs = _add_message(
            {"messages": msgs},
            "Research_Agent",
            "INVESTIGATE",
            f"SYSTEMIC PATTERN DETECTED: {pat['affected_count']} cases share signature '{pat['error_signature']}'.",
            level="WARNING",
            data=pat
        )

    return {
        "evidence": evidence,
        "before_state": before_snap,
        "current_stage": "PLAN",
        "messages": msgs
    }

def plan_node(state: AgentState) -> Dict[str, Any]:
    text = state["complaint_text"]
    ctx = state["context"]
    replan_trigger = state.get("replan_trigger")

    plan_obj = planner_agent.plan(text, ctx, replan_trigger=replan_trigger)

    stage_label = "REPLAN" if replan_trigger else "PLAN"
    plan_note = f"Replanned workflow: {plan_obj.goal} ({len(plan_obj.steps)} steps)" if replan_trigger else f"Formulated execution plan with {len(plan_obj.steps)} tasks."

    msgs = _add_message(
        state,
        "Planner_Agent",
        stage_label,
        plan_note,
        level="INFO",
        data=plan_obj.model_dump()
    )

    return {
        "plan": plan_obj.model_dump(),
        "replan_trigger": None,
        "current_stage": "DECIDE",
        "messages": msgs
    }

def critic_validation_node(state: AgentState) -> Dict[str, Any]:
    plan_dict = state["plan"]
    steps = [StepAction(**s) for s in plan_dict.get("steps", [])]
    plan_obj = StructuredPlan(
        plan_id=plan_dict.get("plan_id", "PLAN-01"),
        goal=plan_dict.get("goal", ""),
        issue_category=plan_dict.get("issue_category", ""),
        steps=steps
    )
    evidence = state["evidence"]

    validation = critic_agent.validate_pre_execution(plan_obj, evidence)
    v_dict = validation.model_dump()

    level = "SUCCESS" if validation.decision == "APPROVE" else ("WARNING" if validation.decision == "REJECT" else "ERROR")
    msgs = _add_message(
        state,
        "Critic_Agent",
        "DECIDE",
        f"Pre-Execution Gate: {validation.decision} — {validation.reason}",
        level=level,
        data=v_dict
    )

    return {
        "validation_result": v_dict,
        "messages": msgs
    }

def route_after_validation(state: AgentState) -> str:
    validation = state.get("validation_result", {})
    decision = validation.get("decision", "APPROVE")
    replan_count = state.get("replan_count", 0)

    if decision == "REJECT":
        if replan_count < 2:
            return "replan"
        else:
            return "escalate"
    elif decision == "ESCALATE":
        return "escalate"
    return "execute"

def replan_node(state: AgentState) -> Dict[str, Any]:
    v_dict = state.get("validation_result", {})
    new_replan_count = state.get("replan_count", 0) + 1

    msgs = _add_message(
        state,
        "Critic_Agent",
        "REPLAN",
        f"CRITIC REJECTION: Triggering Replanning Loop (Cycle {new_replan_count}/2). Reason: {v_dict.get('reason')}",
        level="WARNING"
    )

    replan_trigger = {
        "cycle": new_replan_count,
        "reason": v_dict.get("reason"),
        "guidance": v_dict.get("replan_guidance"),
        "previous_decision": "REJECT"
    }

    return {
        "replan_count": new_replan_count,
        "replan_trigger": replan_trigger,
        "current_stage": "REPLAN",
        "messages": msgs
    }

def escalate_node(state: AgentState) -> Dict[str, Any]:
    v_dict = state.get("validation_result", {})
    case_id = state.get("case_id", "CASE-001")
    cid = state.get("customer_id", "CUST-103")

    # Call escalation tool
    evidence_pack = {
        "complaint": state["complaint_text"],
        "context": state["context"],
        "critic_evaluation": v_dict
    }
    escalation_res = critic_agent.validate_pre_execution(
        StructuredPlan(plan_id="ESC", goal="Escalate", issue_category="ESC", steps=[]),
        state["evidence"]
    )

    auto_res = business_automation_agent.automate_resolution_workflow(
        case_id=case_id,
        customer_id=cid,
        resolution_type="ESCALATED",
        details={"reason": v_dict.get("reason")}
    )

    msgs = _add_message(
        state,
        "Business_Automation_Agent",
        "RESOLVE",
        f"Autonomous disbursement safely halted. Case {case_id} escalated to Tier-2 Operations Lead.",
        level="ERROR",
        data=auto_res
    )

    after_snap = db.get_snapshot()

    return {
        "workflow_result": auto_res,
        "final_status": "ESCALATED_TO_HUMAN",
        "current_stage": "RESOLVE",
        "after_state": after_snap,
        "messages": msgs
    }

def execute_node(state: AgentState) -> Dict[str, Any]:
    plan_dict = state["plan"]
    steps = [StepAction(**s) for s in plan_dict.get("steps", [])]

    # Executor Agent runs each action sequentially
    exec_results = executor_agent.execute_plan(steps)
    res_dicts = [r.model_dump() for r in exec_results]

    msgs = list(state.get("messages", []))
    for res in exec_results:
        lvl = "SUCCESS" if res.success else "ERROR"
        msgs.append({
            "agent_name": "Executor_Agent",
            "stage": "EXECUTE",
            "message": f"Tool Execution [{res.tool_name}]: {res.details}",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": lvl,
            "data": res.state_changes
        })

    return {
        "execution_results": res_dicts,
        "current_stage": "VERIFY",
        "messages": msgs
    }

def critic_verification_node(state: AgentState) -> Dict[str, Any]:
    exec_results = state.get("execution_results", [])
    ctx = state.get("context", {})

    verification = critic_agent.verify_post_execution(exec_results, ctx)
    v_dict = verification.model_dump()

    msgs = _add_message(
        state,
        "Critic_Agent",
        "VERIFY",
        f"Post-Execution Verification: {verification.summary} (Hash: {verification.audit_hash})",
        level="SUCCESS" if verification.verified else "ERROR",
        data=v_dict
    )

    return {
        "verification_result": v_dict,
        "current_stage": "RESOLVE",
        "messages": msgs
    }

def business_automation_node(state: AgentState) -> Dict[str, Any]:
    case_id = state.get("case_id", "CASE-001")
    cid = state.get("customer_id", "CUST-101")
    ctx = state.get("context", {})
    evidence = state.get("evidence", {})
    replan_count = state.get("replan_count", 0)

    # Check if systemic incident
    software_res = None
    if evidence.get("systemic_pattern") and evidence["systemic_pattern"].get("is_systemic"):
        pat = evidence["systemic_pattern"]
        auto_res = business_automation_agent.handle_systemic_cluster(
            cluster_key=pat["cluster_key"],
            error_signature=pat["error_signature"],
            affected_cases=pat["affected_case_ids"]
        )
        msgs = _add_message(
            state,
            "Business_Automation_Agent",
            "RESOLVE",
            f"Master Incident {auto_res['incident_id']} created. Linked {auto_res['linked_cases_count']} customer cases. Notification broadcasted.",
            level="SUCCESS",
            data=auto_res
        )

        # Trigger Software Development Agent for rule synthesis & validation
        software_res = software_dev_agent.synthesize_and_validate_rule(pat["error_signature"])
        rule = software_res["rule"]
        msgs = _add_message(
            {"messages": msgs},
            "Software_Development_Agent",
            "CONTINUOUS_IMPROVEMENT",
            f"Synthesized rule {rule['rule_id']} for {pat['error_signature']}. Validation Test Accuracy: {rule['accuracy_score']*100:.1f}%. Committed to Rule Engine.",
            level="SUCCESS",
            data=software_res
        )
        final_status = "SYSTEMIC_INCIDENT_ORCHESTRATED"

    elif replan_count > 0:
        # Replanned resolution with existing refund tracking
        refund_info = db.get_refund_by_transaction(ctx.get("transaction_id", ""))
        auto_res = business_automation_agent.automate_resolution_workflow(
            case_id=case_id,
            customer_id=cid,
            resolution_type="REFUND_ALREADY_EXISTS",
            details={
                "refund_id": refund_info.get("refund_id") if refund_info else "RF-EXISTS",
                "arn": refund_info.get("arn") if refund_info else "ARN-PENDING"
            }
        )
        msgs = _add_message(
            state,
            "Business_Automation_Agent",
            "RESOLVE",
            f"Resolved inquiry with existing tracking ARN. Case {case_id} marked RESOLVED. Notification dispatched.",
            level="SUCCESS",
            data=auto_res
        )
        final_status = "RESOLVED_WITH_EXISTING_STATUS"

    else:
        # Standard autonomous resolution
        refund_info = db.get_refund_by_transaction(ctx.get("transaction_id", ""))
        auto_res = business_automation_agent.automate_resolution_workflow(
            case_id=case_id,
            customer_id=cid,
            resolution_type="REFUND_SUCCESS",
            details={
                "amount": ctx.get("amount", 2499.0),
                "refund_id": refund_info.get("refund_id") if refund_info else "RF-SUCCESS",
                "arn": refund_info.get("arn") if refund_info else "ARN-SUCCESS"
            }
        )
        msgs = _add_message(
            state,
            "Business_Automation_Agent",
            "RESOLVE",
            f"Autonomous workflow executed: Case {case_id} closed. Refund confirmation SMS sent to customer.",
            level="SUCCESS",
            data=auto_res
        )
        final_status = "RESOLVED_AUTONOMOUSLY"

    after_snap = db.get_snapshot()

    return {
        "workflow_result": auto_res,
        "software_dev_result": software_res,
        "final_status": final_status,
        "after_state": after_snap,
        "current_stage": "RESOLVE",
        "messages": msgs
    }

def build_resolvex_graph():
    """
    Constructs the LangGraph StateGraph orchestration pipeline.
    """
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("research", research_node)
    workflow.add_node("planner", plan_node)
    workflow.add_node("critic_validation", critic_validation_node)
    workflow.add_node("replan", replan_node)
    workflow.add_node("escalate", escalate_node)
    workflow.add_node("executor", execute_node)
    workflow.add_node("critic_verification", critic_verification_node)
    workflow.add_node("business_automation", business_automation_node)

    # Set Entry Point
    workflow.set_entry_point("research")

    # Edges
    workflow.add_edge("research", "planner")
    workflow.add_edge("planner", "critic_validation")

    # Conditional Routing from Critic Validation
    workflow.add_conditional_edges(
        "critic_validation",
        route_after_validation,
        {
            "replan": "replan",
            "escalate": "escalate",
            "execute": "executor"
        }
    )

    # Replanning Loop: back to planner
    workflow.add_edge("replan", "planner")

    # Execution Pipeline
    workflow.add_edge("executor", "critic_verification")
    workflow.add_edge("critic_verification", "business_automation")
    workflow.add_edge("business_automation", END)
    workflow.add_edge("escalate", END)

    return workflow.compile()

# Global compiled graph
resolvex_graph = build_resolvex_graph()

def run_resolution_flow(complaint_text: str, context: Dict[str, Any]) -> AgentState:
    """Helper entry point to execute resolution pipeline."""
    initial_state: AgentState = {
        "complaint_text": complaint_text,
        "case_id": context.get("case_id", "CASE-001"),
        "customer_id": context.get("customer_id", "CUST-101"),
        "context": context,
        "evidence": {},
        "plan": None,
        "replan_count": 0,
        "replan_trigger": None,
        "validation_result": None,
        "execution_results": [],
        "verification_result": None,
        "workflow_result": None,
        "software_dev_result": None,
        "messages": [],
        "current_stage": "UNDERSTAND",
        "final_status": "PENDING",
        "before_state": {},
        "after_state": {}
    }

    final_output = resolvex_graph.invoke(initial_state)

    # Attach customer-friendly response generated by LLM reasoning
    try:
        from src.llm.client import llm_client
        from src.db.sqlite_store import sqlite_store

        txn_id = context.get("transaction_id", "")
        refund_record = db.get_refund_by_transaction(txn_id)
        final_stat = final_output.get("final_status", "RESOLVED_AUTONOMOUSLY")
        
        cust_resp = llm_client.generate_customer_response(
            complaint_text,
            final_stat,
            refund_record or {"amount": context.get("amount", 2499.0)},
            {"case_id": final_output.get("case_id"), "incident_id": "INC-2026-SYS"}
        )
        final_output["customer_response"] = cust_resp

        # Sync to user's isolated SQLite database
        user_id = context.get("user_id", "USER-DEMO-001")
        if refund_record:
            sqlite_store.record_refund(
                user_id,
                txn_id,
                refund_record.get("amount", context.get("amount", 2499.0)),
                refund_record.get("arn", "ARN-UPI-SUCCESS"),
                refund_record.get("refund_id", "RF-NEW")
            )
    except Exception as e:
        logger.warning(f"Error enriching customer response: {e}")

    return final_output

