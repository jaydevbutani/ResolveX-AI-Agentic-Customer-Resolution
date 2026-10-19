from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StepAction(BaseModel):
    step_id: int
    tool_name: str
    description: str
    target_params: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""

class StructuredPlan(BaseModel):
    plan_id: str
    goal: str
    issue_category: str
    steps: List[StepAction]
    requires_replanning: bool = False
    replan_reason: Optional[str] = None

class ValidationCheck(BaseModel):
    check_name: str
    passed: bool
    details: str

class ValidationResult(BaseModel):
    decision: str = "APPROVE"  # "APPROVE", "REJECT", "ESCALATE"
    confidence_score: float = 1.0
    reason: str
    replan_guidance: Optional[str] = None
    policy_citation: Optional[str] = None
    checks: List[ValidationCheck] = Field(default_factory=list)

class ExecutionResult(BaseModel):
    step_id: int
    tool_name: str
    success: bool
    state_changes: Dict[str, Any] = Field(default_factory=dict)
    details: str
    error: Optional[str] = None

class VerificationResult(BaseModel):
    verified: bool
    state_integrity_passed: bool
    audit_hash: str
    summary: str

class AgentMessage(BaseModel):
    agent_name: str
    timestamp: str
    stage: str
    message: str
    structured_data: Optional[Dict[str, Any]] = None
    level: str = "INFO" # "INFO", "SUCCESS", "WARNING", "ERROR"

class SystemicPattern(BaseModel):
    is_systemic: bool
    cluster_key: str
    affected_count: int
    error_signature: str
    recommended_action: str
    affected_case_ids: List[str] = Field(default_factory=list)

class GeneratedRule(BaseModel):
    rule_id: str
    name: str
    description: str
    condition: Dict[str, Any]
    action: str
    accuracy_score: float
    tested_cases: int
    status: str = "ACTIVE"
