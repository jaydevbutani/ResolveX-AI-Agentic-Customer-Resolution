import json
import logging
from typing import Dict, Any, Optional
from src.llm.client import llm_client
from src.models.schemas import StructuredPlan, StepAction

logger = logging.getLogger("ResolveX.Planner")

class PlannerAgent:
    """
    Planner Agent:
    Understands customer complaint, decomposes problem into executable task graph,
    and dynamically replans when Critic rejects an unsafe or redundant action.
    """
    def __init__(self):
        self.name = "Planner_Agent"

    def plan(self, issue_description: str, context: Dict[str, Any], replan_trigger: Optional[Dict[str, Any]] = None) -> StructuredPlan:
        system_prompt = (
            "You are the Planner Agent for ResolveX AI, an autonomous customer issue resolution engine.\n"
            "Your responsibility is to analyze the customer complaint and research context, then decompose it "
            "into a machine-actionable sequence of tool executions.\n"
            "Available tools: get_transaction, get_order, check_refund_policy, check_previous_refund, "
            "calculate_refund, initiate_refund, get_refund_status, update_order_status, update_case_status, "
            "send_customer_notification, escalate_to_human, cluster_systemic_cases, create_incident, link_related_cases, synthesize_detection_rule.\n"
            "Return valid JSON adhering to the StructuredPlan schema."
        )

        replan_text = f"REPLAN_DIRECTIVE: {json.dumps(replan_trigger, indent=2)}" if replan_trigger else "INITIAL_DISPATCH: True"
        prompt = f"""
Customer Issue: "{issue_description}"
Context Data: {json.dumps(context, indent=2)}
{replan_text}

Generate a clear, minimal, safety-conscious structured plan.
"""
        response = llm_client.query(prompt, system_prompt)
        structured = response.get("structured", {})

        # Ensure valid StructuredPlan
        if "steps" in structured and isinstance(structured["steps"], list):
            steps = []
            for s in structured["steps"]:
                steps.append(StepAction(
                    step_id=s.get("step_id", len(steps) + 1),
                    tool_name=s.get("tool_name", ""),
                    description=s.get("description", ""),
                    target_params=s.get("target_params", {}),
                    rationale=s.get("rationale", "")
                ))
            return StructuredPlan(
                plan_id=structured.get("plan_id", "PLAN-GEN-01"),
                goal=structured.get("goal", "Resolve customer issue autonomously"),
                issue_category=structured.get("issue_category", "GENERAL_ISSUE"),
                steps=steps,
                requires_replanning=bool(replan_trigger),
                replan_reason=replan_trigger.get("reason") if replan_trigger else None
            )

        # Fallback to standard structured plan
        return StructuredPlan(
            plan_id="PLAN-DEFAULT",
            goal="Investigate and resolve customer issue",
            issue_category="PAYMENT_ORDER_MISMATCH",
            steps=[
                StepAction(step_id=1, tool_name="get_transaction", description="Verify payment status", target_params={"transaction_id": context.get("transaction_id", "TXN-8821")}),
                StepAction(step_id=2, tool_name="get_order", description="Verify order status", target_params={"order_id": context.get("order_id", "ORD-5501")}),
                StepAction(step_id=3, tool_name="check_refund_policy", description="Query policy knowledge base", target_params={"policy_id": "POL-REF-01"}),
                StepAction(step_id=4, tool_name="check_previous_refund", description="Guard against duplicate disbursement", target_params={"transaction_id": context.get("transaction_id", "TXN-8821")}),
                StepAction(step_id=5, tool_name="initiate_refund", description="Initiate autonomous refund", target_params={"transaction_id": context.get("transaction_id", "TXN-8821"), "amount": 2499.0}),
                StepAction(step_id=6, tool_name="get_refund_status", description="Verify gateway settlement state", target_params={"transaction_id": context.get("transaction_id", "TXN-8821")}),
                StepAction(step_id=7, tool_name="send_customer_notification", description="Notify customer with confirmation", target_params={"channel": "SMS"})
            ]
        )

# Global Planner instance
planner_agent = PlannerAgent()
