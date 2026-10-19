import re
from typing import Dict, Any, List, Optional
from src.rag.policy_kb import policy_kb
from src.db.store import db
from src.models.schemas import SystemicPattern

class ResearchAgent:
    """
    Research Agent:
    - Synthesizes unstructured customer complaints
    - Retrieves grounded policy articles via RAG
    - Gathers transactional and customer trust telemetry
    - Identifies systemic incident clusters
    """
    def __init__(self):
        self.name = "Research_Agent"

    def analyze_complaint(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        extracted_entities = self._extract_entities(text, context)

        # Retrieve relevant policies via RAG
        policies = policy_kb.retrieve(text + " " + extracted_entities.get("issue_type", ""), top_k=2)

        # Pull ground-truth context from store
        cust_profile = None
        txn_data = None
        ord_data = None
        prev_refund = None

        if extracted_entities.get("customer_id"):
            cust_profile = db.get_customer(extracted_entities["customer_id"])

        if extracted_entities.get("transaction_id"):
            txn_data = db.get_transaction(extracted_entities["transaction_id"])
            if txn_data:
                prev_refund = db.get_refund_by_transaction(extracted_entities["transaction_id"])
                if not ord_data and txn_data.get("order_id"):
                    ord_data = db.get_order(txn_data["order_id"])

        if extracted_entities.get("order_id") and not ord_data:
            ord_data = db.get_order(extracted_entities["order_id"])

        # Check for systemic pattern
        systemic_pattern = self.detect_systemic_cluster(text=text, txn_data=txn_data)

        evidence_dossier = {
            "extracted_entities": extracted_entities,
            "grounded_policies": policies,
            "primary_policy": policies[0] if policies else None,
            "customer_profile": cust_profile,
            "transaction_record": txn_data,
            "order_record": ord_data,
            "previous_refund": prev_refund,
            "systemic_pattern": systemic_pattern.model_dump() if systemic_pattern else None
        }

        return evidence_dossier

    def detect_systemic_cluster(self, error_code: str = "PG_TIMEOUT_504", text: str = "", txn_data: Optional[Dict[str, Any]] = None) -> Optional[SystemicPattern]:
        """Scans the case registry to see if multiple cases share the same root cause."""
        # Only evaluate systemic cluster if the current issue involves the error code or mentions systemic/outage/multiple
        is_relevant = (
            "systemic" in text.lower() or 
            "outage" in text.lower() or 
            "multiple" in text.lower() or 
            (txn_data and txn_data.get("error_code") == error_code)
        )
        if not is_relevant:
            return None

        all_cases = db.get_all_cases()
        matching_cases = []
        for c in all_cases:
            if error_code in c.get("description", "") or c.get("issue_type") == "PAYMENT_CAPTURE_WITHOUT_ORDER":
                matching_cases.append(c["case_id"])

        if len(matching_cases) >= 5:
            return SystemicPattern(
                is_systemic=True,
                cluster_key=f"CLUSTER-{error_code}",
                affected_count=len(matching_cases),
                error_signature=error_code,
                recommended_action="TRIGGER_PARENT_INCIDENT_WORKFLOW",
                affected_case_ids=matching_cases
            )
        return None

    def _extract_entities(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        entities = dict(context)

        # Extract amount if present (e.g. ₹2,499 or INR 48,500)
        amt_match = re.search(r'(?:₹|INR|rs\.?)\s*([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)
        if amt_match and "amount" not in entities:
            clean_num = amt_match.group(1).replace(",", "")
            entities["amount"] = float(clean_num)

        # Extract IDs
        txn_match = re.search(r'(TXN-\d+)', text, re.IGNORECASE)
        if txn_match and "transaction_id" not in entities:
            entities["transaction_id"] = txn_match.group(1).upper()

        ord_match = re.search(r'(ORD-\d+)', text, re.IGNORECASE)
        if ord_match and "order_id" not in entities:
            entities["order_id"] = ord_match.group(1).upper()

        cust_match = re.search(r'(CUST-\d+)', text, re.IGNORECASE)
        if cust_match and "customer_id" not in entities:
            entities["customer_id"] = cust_match.group(1).upper()

        # Issue type classification
        text_lower = text.lower()
        if "deducted" in text_lower and ("failed" in text_lower or "drop" in text_lower):
            entities["issue_type"] = "MONEY_DEDUCTED_ORDER_FAILED"
        elif "already" in text_lower or "status" in text_lower:
            entities["issue_type"] = "REFUND_STATUS_INQUIRY"
        elif "subscription" in text_lower or "recurring" in text_lower:
            entities["issue_type"] = "SUBSCRIPTION_BILLING_DISPUTE"
        elif "systemic" in text_lower or "multiple" in text_lower:
            entities["issue_type"] = "SYSTEMIC_INCIDENT"
        else:
            entities["issue_type"] = "GENERAL_COMPLAINT"

        return entities

# Global Research instance
research_agent = ResearchAgent()
