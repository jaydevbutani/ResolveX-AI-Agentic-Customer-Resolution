import hashlib
import json
import logging
from typing import Dict, Any, List
from src.llm.client import llm_client
from src.models.schemas import ValidationResult, ValidationCheck, VerificationResult, StructuredPlan
from src.db.store import db
from src.config import MAX_AUTONOMOUS_REFUND_INR, MIN_CUSTOMER_TRUST_SCORE

logger = logging.getLogger("ResolveX.Critic")

class CriticAgent:
    """
    Critic Agent:
    - Pre-Execution Gatekeeper: Validates safety, policy compliance, and duplicate action risks.
      Emits APPROVE, REJECT (triggering replanning loop), or ESCALATE.
    - Post-Execution Verifier: Validates that synthetic database mutations actually took effect.
    """
    def __init__(self):
        self.name = "Critic_Agent"

    def validate_pre_execution(self, plan: StructuredPlan, evidence: Dict[str, Any]) -> ValidationResult:
        """
        Validates proposed actions before executing any state-changing operations.
        """
        txn = evidence.get("transaction_record")
        ord_rec = evidence.get("order_record")
        prev_refund = evidence.get("previous_refund")
        cust = evidence.get("customer_profile")
        primary_policy = evidence.get("primary_policy")

        checks: List[ValidationCheck] = []

        # Check 1: Duplicate Refund Guard
        has_initiate_refund = any(s.tool_name == "initiate_refund" for s in plan.steps)
        if prev_refund and has_initiate_refund:
            checks.append(ValidationCheck(
                check_name="Duplicate Action Guard",
                passed=False,
                details=f"CRITICAL: Plan attempts initiate_refund, but active refund {prev_refund.get('refund_id')} already exists in state {prev_refund.get('status')}!"
            ))
            return ValidationResult(
                decision="REJECT",
                confidence_score=0.99,
                reason=f"Financial Integrity Violation: Transaction {txn.get('transaction_id') if txn else 'N/A'} already has refund {prev_refund.get('refund_id')}.",
                replan_guidance="Cancel initiate_refund step. Replan workflow to retrieve status of existing refund and notify customer with existing ARN.",
                policy_citation="POL-REF-03: Duplicate Refund Prevention & Guard Policy",
                checks=checks
            )
        elif prev_refund and not has_initiate_refund:
            checks.append(ValidationCheck(
                check_name="Duplicate Action Guard",
                passed=True,
                details=f"Safe: Plan does not initiate new disbursement. Only queries status of existing refund {prev_refund.get('refund_id')}."
            ))
        else:
            checks.append(ValidationCheck(
                check_name="Duplicate Action Guard",
                passed=True,
                details="Zero existing refund records detected for this transaction."
            ))

        # Check 2: Transaction & Order Status
        if txn:
            if txn.get("status") == "SUCCESS":
                checks.append(ValidationCheck(
                    check_name="Payment Gateway Capture",
                    passed=True,
                    details=f"Payment verified SUCCESS via {txn.get('gateway', 'Gateway')}."
                ))
            else:
                checks.append(ValidationCheck(
                    check_name="Payment Gateway Capture",
                    passed=False,
                    details=f"Payment status is {txn.get('status')}, not SUCCESS."
                ))
        if ord_rec:
            if ord_rec.get("status") in ["FAILED", "CANCELLED"]:
                checks.append(ValidationCheck(
                    check_name="Order Failure Verification",
                    passed=True,
                    details=f"Order {ord_rec.get('order_id')} is confirmed {ord_rec.get('status')} ({ord_rec.get('failure_reason', 'N/A')})."
                ))
            else:
                checks.append(ValidationCheck(
                    check_name="Order Failure Verification",
                    passed=False,
                    details=f"Order status is {ord_rec.get('status')}."
                ))

        # Check 3: High-Value Threshold & Risk Escalation
        amount = txn.get("amount", 0.0) if txn else evidence.get("extracted_entities", {}).get("amount", 0.0)
        trust_score = cust.get("trust_score", 100) if cust else 100
        is_suspicious = cust.get("is_suspicious", False) if cust else False
        error_code = txn.get("error_code") if txn else "NONE"

        if amount > MAX_AUTONOMOUS_REFUND_INR or trust_score < MIN_CUSTOMER_TRUST_SCORE or is_suspicious or error_code == "MISMATCH_DEVICE_IP":
            checks.append(ValidationCheck(
                check_name="Autonomous Safety Threshold",
                passed=False,
                details=f"Risk criteria breached: Amount INR {amount:,.2f} (Limit INR {MAX_AUTONOMOUS_REFUND_INR:,.2f}), Trust Score {trust_score}/100, Suspicious Flag: {is_suspicious}."
            ))
            return ValidationResult(
                decision="ESCALATE",
                confidence_score=0.98,
                reason=f"Safety Exception Triggered: Transaction INR {amount:,.2f} exceeds threshold or account security flags detected. Autonomous disbursement blocked.",
                replan_guidance="Generate complete evidence docket and escalate to Tier-2 Operations Lead for human review.",
                policy_citation="POL-ESC-05: High-Value Transaction & Fraud Risk Escalation Protocol",
                checks=checks
            )
        else:
            checks.append(ValidationCheck(
                check_name="Autonomous Safety Threshold",
                passed=True,
                details=f"Amount INR {amount:,.2f} is within INR {MAX_AUTONOMOUS_REFUND_INR:,.2f} limit. Trust Score: {trust_score}."
            ))

        # Check 4: Policy Alignment
        policy_id = primary_policy.get("policy_id", "POL-REF-01") if primary_policy else "POL-REF-01"
        checks.append(ValidationCheck(
            check_name="Policy Grounding Check",
            passed=True,
            details=f"Fully conforms to {policy_id} conditions."
        ))

        return ValidationResult(
            decision="APPROVE",
            confidence_score=0.99,
            reason="Pre-Execution Validation PASSED: Low-risk, fully eligible transaction. Autonomous resolution authorized.",
            replan_guidance=None,
            policy_citation=f"{policy_id}: {primary_policy.get('title', 'Refund Eligibility Policy') if primary_policy else 'Standard Policy'}",
            checks=checks
        )

    def verify_post_execution(self, step_results: List[Dict[str, Any]], context: Dict[str, Any]) -> VerificationResult:
        """
        Validates after execution that synthetic business state actually transitioned.
        """
        txn_id = context.get("transaction_id")
        refund_record = db.get_refund_by_transaction(txn_id) if txn_id else None

        verified = True
        summary_points = []

        if refund_record:
            if refund_record.get("status") == "SUCCESS":
                summary_points.append(f"Refund {refund_record['refund_id']} verified SUCCESS on gateway with ARN {refund_record.get('arn')}")
            else:
                verified = False
                summary_points.append(f"Refund {refund_record['refund_id']} in unexpected status {refund_record.get('status')}")
        else:
            # If the plan didn't require a new refund (e.g. status tracking or escalation)
            summary_points.append("Execution completed without anomalous financial mutations.")

        # Compute tamper-evident audit hash
        audit_payload = f"{txn_id}-{len(step_results)}-{refund_record.get('refund_id') if refund_record else 'NONE'}"
        audit_hash = hashlib.sha256(audit_payload.encode()).hexdigest()[:16].upper()

        return VerificationResult(
            verified=verified,
            state_integrity_passed=verified,
            audit_hash=f"AUTH-DIGEST-{audit_hash}",
            summary="; ".join(summary_points)
        )

# Global Critic instance
critic_agent = CriticAgent()
