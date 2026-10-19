from typing import Dict, Any, List, Optional
from src.db.store import db
from src.rag.policy_kb import policy_kb
from src.config import MAX_AUTONOMOUS_REFUND_INR, MIN_CUSTOMER_TRUST_SCORE

def get_customer(customer_id: str = "CUST-101") -> Dict[str, Any]:
    """Retrieve customer account and trust score profile."""
    cust = db.get_customer(customer_id)
    if not cust:
        return {"status": "ERROR", "message": f"Customer {customer_id} not found."}
    return {"status": "SUCCESS", "customer": cust}

def get_transaction(transaction_id: str = "TXN-8821") -> Dict[str, Any]:
    """Retrieve simulated payment gateway transaction."""
    txn = db.get_transaction(transaction_id)
    if not txn:
        return {"status": "ERROR", "message": f"Transaction {transaction_id} not found."}
    return {"status": "SUCCESS", "transaction": txn}

def get_order(order_id: str = "ORD-5501") -> Dict[str, Any]:
    """Retrieve simulated e-commerce order and fulfillment status."""
    ord_rec = db.get_order(order_id)
    if not ord_rec:
        return {"status": "ERROR", "message": f"Order {order_id} not found."}
    return {"status": "SUCCESS", "order": ord_rec}

def get_subscription(subscription_id: str = "SUB-101") -> Dict[str, Any]:
    """Retrieve recurring billing subscription state."""
    sub = db.get_subscription(subscription_id)
    if not sub:
        return {"status": "ERROR", "message": f"Subscription {subscription_id} not found."}
    return {"status": "SUCCESS", "subscription": sub}

def check_refund_policy(policy_id: Optional[str] = None, query: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve grounded refund policy via Knowledge Base RAG."""
    target = policy_id or query or "POL-REF-01"
    if target.startswith("POL-"):
        pol = policy_kb.get_policy_by_id(target)
        if pol:
            return {"status": "SUCCESS", "policy": pol}
    matches = policy_kb.retrieve(target, top_k=2)
    return {"status": "SUCCESS", "matched_policies": matches}

def check_previous_refund(transaction_id: str = "TXN-8821") -> Dict[str, Any]:
    """Financial integrity check: ensure no existing refund record is already attached."""
    existing = db.get_refund_by_transaction(transaction_id)
    if existing:
        return {
            "status": "EXISTS",
            "has_previous_refund": True,
            "refund": existing,
            "message": f"Previous refund {existing['refund_id']} found with status {existing['status']}."
        }
    return {
        "status": "NOT_FOUND",
        "has_previous_refund": False,
        "message": "No previous refund record found. Eligible for processing."
    }

def check_refund_eligibility(transaction_id: str = "TXN-8821", order_id: Optional[str] = None) -> Dict[str, Any]:
    txn = db.get_transaction(transaction_id)
    if not txn:
        return {"eligible": False, "reason": f"Transaction {transaction_id} not found."}

    if txn.get("status") != "SUCCESS":
        return {"eligible": False, "reason": f"Payment is not in SUCCESS status (current: {txn.get('status')})."}

    actual_order_id = order_id or txn.get("order_id")
    if actual_order_id:
        ord_rec = db.get_order(actual_order_id)
        if ord_rec and ord_rec.get("status") not in ["FAILED", "CANCELLED"]:
            return {"eligible": False, "reason": f"Order {actual_order_id} is in status {ord_rec.get('status')}, not FAILED."}

    prev_refund = db.get_refund_by_transaction(transaction_id)
    if prev_refund:
        return {
            "eligible": False,
            "reason": f"Refund {prev_refund['refund_id']} is already {prev_refund['status']}.",
            "existing_refund": prev_refund
        }

    cust = db.get_customer(txn.get("customer_id"))
    amount = txn.get("amount", 0.0)

    if amount > MAX_AUTONOMOUS_REFUND_INR:
        return {
            "eligible": False,
            "requires_human_escalation": True,
            "reason": f"Amount INR {amount:,.2f} exceeds autonomous limit INR {MAX_AUTONOMOUS_REFUND_INR:,.2f}."
        }

    if cust and (cust.get("trust_score", 100) < MIN_CUSTOMER_TRUST_SCORE or cust.get("is_suspicious")):
        return {
            "eligible": False,
            "requires_human_escalation": True,
            "reason": f"Customer trust score ({cust.get('trust_score')}) below threshold or suspicious security flag present."
        }

    return {
        "eligible": True,
        "amount": amount,
        "currency": txn.get("currency", "INR"),
        "reason": "Meets autonomous refund criteria: payment captured, order failed, no prior refund, within financial limit."
    }

def calculate_refund(transaction_id: str = "TXN-8821") -> Dict[str, Any]:
    txn = db.get_transaction(transaction_id)
    if not txn:
        return {"status": "ERROR", "message": "Transaction not found"}
    base_amount = txn.get("amount", 0.0)
    return {
        "status": "SUCCESS",
        "transaction_id": transaction_id,
        "base_amount": base_amount,
        "deductions": 0.0,
        "fee_waiver": 0.0,
        "total_refundable_amount": base_amount,
        "currency": txn.get("currency", "INR")
    }

def initiate_refund(transaction_id: str = "TXN-8821", amount: float = 2499.0, reason: str = "Autonomous Agent Resolution") -> Dict[str, Any]:
    try:
        record = db.initiate_refund(transaction_id, amount, reason, actor="Executor_Agent")
        return {
            "status": "SUCCESS",
            "refund_id": record["refund_id"],
            "amount": record["amount"],
            "arn": record["arn"],
            "gateway_status": record["status"],
            "message": f"Refund {record['refund_id']} for INR {amount:,.2f} successfully initiated on {record['gateway']}."
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

def get_refund_status(transaction_id: Optional[str] = None, refund_id: Optional[str] = None) -> Dict[str, Any]:
    record = None
    if refund_id:
        record = db.get_refund(refund_id)
    elif transaction_id:
        record = db.get_refund_by_transaction(transaction_id)

    if not record:
        return {"status": "NOT_FOUND", "message": "No refund record located."}

    return {
        "status": "SUCCESS",
        "refund_id": record["refund_id"],
        "refund_status": record["status"],
        "amount": record["amount"],
        "arn": record.get("arn"),
        "gateway": record.get("gateway"),
        "initiated_at": record.get("initiated_at"),
        "estimated_credit": record.get("estimated_credit")
    }

def update_order_status(order_id: str = "ORD-5501", status: str = "FAILED_REFUNDED", notes: str = "Updated by ResolveX Agent") -> Dict[str, Any]:
    try:
        ord_rec = db.update_order_status(order_id, status, notes, actor="Executor_Agent")
        return {"status": "SUCCESS", "order_id": order_id, "new_status": ord_rec["status"]}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

def update_case_status(case_id: str = "CASE-001", status: str = "RESOLVED", resolution_summary: str = "Resolved autonomously by ResolveX AI", parent_incident_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        case = db.update_case_status(case_id, status, resolution_summary, parent_incident_id, actor="Business_Automation_Agent")
        return {"status": "SUCCESS", "case_id": case_id, "case_status": case["status"]}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

def send_customer_notification(customer_id: str = "CUST-101", channel: str = "SMS", subject: str = "Resolution Confirmation", message: str = "Your issue has been resolved.") -> Dict[str, Any]:
    try:
        notif = db.send_notification(customer_id, channel, subject, message, actor="Business_Automation_Agent")
        return {"status": "DELIVERED", "notification_id": notif["notification_id"], "channel": channel}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

def create_incident(title: str = "Systemic Gateway Incident", description: str = "Bulk gateway timeout observed", severity: str = "HIGH", affected_count: int = 50) -> Dict[str, Any]:
    try:
        inc = db.create_incident(title, description, severity, affected_count, actor="Business_Automation_Agent")
        return {"status": "SUCCESS", "incident_id": inc["incident_id"], "severity": severity}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

def link_related_cases(incident_id: str = "INC-2026-SYS", case_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    c_ids = case_ids or [f"CASE-SYS-{i:03d}" for i in range(1, 51)]
    try:
        db.link_cases_to_incident(incident_id, c_ids, actor="Business_Automation_Agent")
        return {"status": "SUCCESS", "incident_id": incident_id, "linked_count": len(c_ids)}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

def escalate_to_human(case_id: str = "CASE-001", reason: str = "High value or security exception", evidence_package: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    summary = f"ESCALATED TO TIER-2 HUMAN LEAD. Reason: {reason}"
    db.update_case_status(case_id, "ESCALATED_TO_HUMAN", summary, actor="Critic_Agent")
    db.log_audit("Critic_Agent", "HUMAN_ESCALATION", f"Case {case_id} blocked from autonomous resolution. Reason: {reason}")
    return {
        "status": "ESCALATED",
        "case_id": case_id,
        "tier": "TIER_2_OPERATIONS",
        "reason": reason,
        "evidence_package": evidence_package or {}
    }
