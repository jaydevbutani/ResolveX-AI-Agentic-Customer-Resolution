from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    complaint_text: str
    case_id: str
    customer_id: str
    context: Dict[str, Any]
    evidence: Dict[str, Any]
    plan: Optional[Dict[str, Any]]
    replan_count: int
    replan_trigger: Optional[Dict[str, Any]]
    validation_result: Optional[Dict[str, Any]]
    execution_results: List[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    workflow_result: Optional[Dict[str, Any]]
    software_dev_result: Optional[Dict[str, Any]]
    messages: List[Dict[str, Any]]
    current_stage: str
    final_status: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
