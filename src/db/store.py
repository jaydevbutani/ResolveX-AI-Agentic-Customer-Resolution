import json
import uuid
import copy
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.config import SYNTHETIC_DB_PATH, SYNTHETIC_DB_TEMPLATE_PATH

class SyntheticDatabase:
    """
    Simulated Enterprise Business Data Store.
    Provides atomic mutations, state diff tracking, audit logging,
    and instantaneous reset for deterministic demos.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SyntheticDatabase, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if SYNTHETIC_DB_PATH.exists():
            with open(SYNTHETIC_DB_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        elif SYNTHETIC_DB_TEMPLATE_PATH.exists():
            with open(SYNTHETIC_DB_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self._save()
        else:
            raise FileNotFoundError("Synthetic database file not found.")

    def _save(self):
        with open(SYNTHETIC_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def reset(self):
        """Reset the synthetic database to pristine factory template."""
        if SYNTHETIC_DB_TEMPLATE_PATH.exists():
            with open(SYNTHETIC_DB_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self._save()
            return True
        return False

    def get_snapshot(self) -> Dict[str, Any]:
        """Returns deep copy snapshot of current state."""
        return copy.deepcopy(self.data)

    def log_audit(self, actor: str, action: str, details: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "details": details
        }
        self.data["audit_logs"].append(entry)
        self._save()

    # --- Read Operations ---
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self.data["customers"].get(customer_id)

    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        return self.data["transactions"].get(transaction_id)

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.data["orders"].get(order_id)

    def get_refund(self, refund_id: str) -> Optional[Dict[str, Any]]:
        return self.data["refunds"].get(refund_id)

    def get_refund_by_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        for r in self.data["refunds"].values():
            if r.get("transaction_id") == transaction_id:
                return r
        return None

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        return self.data["subscriptions"].get(subscription_id)

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self.data["cases"].get(case_id)

    def get_all_cases(self) -> List[Dict[str, Any]]:
        return list(self.data["cases"].values())

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        return list(self.data["transactions"].values())

    def get_all_orders(self) -> List[Dict[str, Any]]:
        return list(self.data["orders"].values())

    def get_all_refunds(self) -> List[Dict[str, Any]]:
        return list(self.data["refunds"].values())

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        return list(self.data["incidents"].values())

    def get_all_notifications(self) -> List[Dict[str, Any]]:
        return list(self.data["notifications"])

    # --- Stateful Business Mutations ---
    def initiate_refund(self, transaction_id: str, amount: float, reason: str, actor: str = "Executor_Agent") -> Dict[str, Any]:
        """
        Executes a real state mutation:
        - Creates a new Refund entity with status 'SUCCESS'
        - Updates the Transaction with the refund reference
        - Emits audit log
        """
        txn = self.get_transaction(transaction_id)
        if not txn:
            raise ValueError(f"Transaction {transaction_id} does not exist.")

        # Guard: check if refund already exists
        existing = self.get_refund_by_transaction(transaction_id)
        if existing:
            raise ValueError(f"Duplicate refund detected! Transaction {transaction_id} already has refund {existing['refund_id']}.")

        refund_id = f"RF-{uuid.uuid4().hex[:6].upper()}"
        arn_code = f"ARN-UPI-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now().isoformat()

        refund_record = {
            "refund_id": refund_id,
            "transaction_id": transaction_id,
            "order_id": txn.get("order_id"),
            "customer_id": txn.get("customer_id"),
            "amount": float(amount),
            "currency": txn.get("currency", "INR"),
            "status": "SUCCESS",
            "arn": arn_code,
            "gateway": txn.get("gateway", "Razorpay"),
            "initiated_at": now_str,
            "estimated_credit": "Instant / Within 24-48 hours",
            "notes": reason
        }

        self.data["refunds"][refund_id] = refund_record
        self.data["transactions"][transaction_id]["refund_id"] = refund_id

        self.log_audit(actor, "INITIATE_REFUND", f"Refund {refund_id} created for {amount} INR on txn {transaction_id}")
        self._save()
        return refund_record

    def update_order_status(self, order_id: str, status: str, notes: str, actor: str = "Executor_Agent") -> Dict[str, Any]:
        ord_record = self.get_order(order_id)
        if not ord_record:
            raise ValueError(f"Order {order_id} not found.")

        old_status = ord_record.get("status")
        ord_record["status"] = status
        ord_record["resolution_notes"] = notes
        ord_record["updated_at"] = datetime.now().isoformat()

        self.log_audit(actor, "UPDATE_ORDER_STATUS", f"Order {order_id} transitioned from {old_status} -> {status}")
        self._save()
        return ord_record

    def update_case_status(self, case_id: str, status: str, resolution_summary: str, parent_incident_id: Optional[str] = None, actor: str = "Business_Automation_Agent") -> Dict[str, Any]:
        case = self.get_case(case_id)
        if not case:
            # Create if not exists
            case = {
                "case_id": case_id,
                "status": status,
                "resolution_summary": resolution_summary,
                "created_at": datetime.now().isoformat(),
                "parent_incident_id": parent_incident_id
            }
            self.data["cases"][case_id] = case
        else:
            case["status"] = status
            case["resolution_summary"] = resolution_summary
            if parent_incident_id:
                case["parent_incident_id"] = parent_incident_id
            if status in ["RESOLVED", "CLOSED"]:
                case["closed_at"] = datetime.now().isoformat()

        self.log_audit(actor, "UPDATE_CASE", f"Case {case_id} marked as {status}")
        self._save()
        return case

    def create_incident(self, title: str, description: str, severity: str, affected_count: int, actor: str = "Business_Automation_Agent") -> Dict[str, Any]:
        inc_id = f"INC-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:4].upper()}"
        incident = {
            "incident_id": inc_id,
            "title": title,
            "description": description,
            "severity": severity,
            "status": "OPEN",
            "affected_count": affected_count,
            "linked_case_ids": [],
            "created_at": datetime.now().isoformat()
        }
        self.data["incidents"][inc_id] = incident
        self.log_audit(actor, "CREATE_INCIDENT", f"Incident {inc_id} opened: {title} ({affected_count} affected)")
        self._save()
        return incident

    def link_cases_to_incident(self, incident_id: str, case_ids: List[str], actor: str = "Business_Automation_Agent"):
        inc = self.data["incidents"].get(incident_id)
        if not inc:
            raise ValueError(f"Incident {incident_id} not found.")

        for cid in case_ids:
            if cid not in inc["linked_case_ids"]:
                inc["linked_case_ids"].append(cid)
            if cid in self.data["cases"]:
                self.data["cases"][cid]["parent_incident_id"] = incident_id
                self.data["cases"][cid]["status"] = "LINKED_TO_INCIDENT"

        self.log_audit(actor, "LINK_CASES", f"Linked {len(case_ids)} cases to incident {incident_id}")
        self._save()

    def send_notification(self, customer_id: str, channel: str, subject: str, message: str, actor: str = "Business_Automation_Agent") -> Dict[str, Any]:
        notif = {
            "notification_id": f"NOTIF-{uuid.uuid4().hex[:6].upper()}",
            "customer_id": customer_id,
            "channel": channel,
            "subject": subject,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "status": "DELIVERED"
        }
        self.data["notifications"].append(notif)
        self.log_audit(actor, "SEND_NOTIFICATION", f"Dispatched {channel} notification to {customer_id}: {subject}")
        self._save()
        return notif

# Global singleton
db = SyntheticDatabase()
