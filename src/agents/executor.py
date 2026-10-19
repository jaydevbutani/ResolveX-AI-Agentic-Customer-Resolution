import logging
from typing import Dict, Any, List
from src.tools import business_tools
from src.models.schemas import StepAction, ExecutionResult

logger = logging.getLogger("ResolveX.Executor")

class ExecutorAgent:
    """
    Executor Agent:
    Executes tasks using functional simulated business tools and APIs.
    Performs real state mutations and returns verifiable execution traces.
    """
    def __init__(self):
        self.name = "Executor_Agent"
        self.tool_dispatch = {
            "get_customer": business_tools.get_customer,
            "get_transaction": business_tools.get_transaction,
            "get_order": business_tools.get_order,
            "get_subscription": business_tools.get_subscription,
            "check_refund_policy": business_tools.check_refund_policy,
            "check_previous_refund": business_tools.check_previous_refund,
            "check_refund_eligibility": business_tools.check_refund_eligibility,
            "calculate_refund": business_tools.calculate_refund,
            "initiate_refund": business_tools.initiate_refund,
            "get_refund_status": business_tools.get_refund_status,
            "update_order_status": business_tools.update_order_status,
            "update_case_status": business_tools.update_case_status,
            "send_customer_notification": business_tools.send_customer_notification,
            "create_incident": business_tools.create_incident,
            "link_related_cases": business_tools.link_related_cases,
            "escalate_to_human": business_tools.escalate_to_human
        }

    def execute_step(self, step: StepAction) -> ExecutionResult:
        tool_fn = self.tool_dispatch.get(step.tool_name)
        if not tool_fn:
            return ExecutionResult(
                step_id=step.step_id,
                tool_name=step.tool_name,
                success=False,
                details=f"Tool '{step.tool_name}' not implemented in tool registry.",
                error="TOOL_NOT_FOUND"
            )

        try:
            # Call tool with target_params
            result = tool_fn(**step.target_params)
            success = result.get("status") not in ["ERROR", "FAILED"]
            return ExecutionResult(
                step_id=step.step_id,
                tool_name=step.tool_name,
                success=success,
                state_changes=result,
                details=result.get("message") or f"Executed {step.tool_name} successfully."
            )
        except Exception as e:
            logger.error(f"Error executing {step.tool_name}: {e}")
            return ExecutionResult(
                step_id=step.step_id,
                tool_name=step.tool_name,
                success=False,
                details=f"Execution failed: {str(e)}",
                error=str(e)
            )

    def execute_plan(self, steps: List[StepAction]) -> List[ExecutionResult]:
        results = []
        for step in steps:
            res = self.execute_step(step)
            results.append(res)
            # If critical action fails, stop execution sequence
            if not res.success and step.tool_name in ["initiate_refund", "escalate_to_human"]:
                break
        return results

# Global Executor instance
executor_agent = ExecutorAgent()
