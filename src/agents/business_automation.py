from typing import Dict, Any, List
from src.db.store import db

class BusinessAutomationAgent:
    """
    Business Automation Agent:
    Executes enterprise workflow automation:
    - Synchronizes CRM case state
    - Dispatches multi-channel customer notifications (SMS/Email)
    - Orchestrates parent incident creation and case clustering
    - Closes operational loops without human overhead
    """
    def __init__(self):
        self.name = "Business_Automation_Agent"

    def automate_resolution_workflow(self, case_id: str, customer_id: str, resolution_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        workflow_actions = []

        # 1. Update CRM Case
        if resolution_type == "REFUND_SUCCESS":
            summary = f"Autonomous resolution completed. Refund {details.get('refund_id')} initiated. ARN: {details.get('arn')}."
            db.update_case_status(case_id, "RESOLVED", summary, actor=self.name)
            workflow_actions.append(f"Updated CRM case {case_id} to RESOLVED.")

            # 2. Send SMS/Email Notification
            sms_body = f"ResolveX Update: ₹{details.get('amount', 2499):,.2f} refund initiated to your original payment method. Ref: {details.get('arn')}. Funds reflect in 24-48h."
            notif = db.send_notification(customer_id, "SMS", "Refund Initiated Successfully", sms_body, actor=self.name)
            workflow_actions.append(f"Dispatched SMS confirmation (Notif ID: {notif['notification_id']}).")

        elif resolution_type == "REFUND_ALREADY_EXISTS":
            summary = f"Inquiry resolved. Customer informed of existing active refund {details.get('refund_id')} (ARN: {details.get('arn')})."
            db.update_case_status(case_id, "RESOLVED", summary, actor=self.name)
            workflow_actions.append(f"Updated CRM case {case_id} to RESOLVED with existing ARN tracking.")

            sms_body = f"ResolveX Update: Your refund {details.get('refund_id')} is already processing under bank ARN {details.get('arn')}. Expected credit: Within 24 hours."
            notif = db.send_notification(customer_id, "SMS", "Refund Status Tracking Update", sms_body, actor=self.name)
            workflow_actions.append(f"Dispatched SMS tracking update (Notif ID: {notif['notification_id']}).")

        elif resolution_type == "ESCALATED":
            summary = f"Case escalated to Tier-2 Operations Lead. Autonomous execution halted. Reason: {details.get('reason')}."
            db.update_case_status(case_id, "ESCALATED_TO_HUMAN", summary, actor=self.name)
            workflow_actions.append(f"Assigned case {case_id} to Tier-2 High-Priority Queue.")

            sms_body = "ResolveX Update: Your inquiry has been routed to our Senior Operations Lead for specialized review. Reference: " + case_id
            db.send_notification(customer_id, "SMS", "Inquiry Under Senior Review", sms_body, actor=self.name)
            workflow_actions.append("Customer informed of priority review timeline.")

        return {
            "status": "SUCCESS",
            "workflow_actions": workflow_actions,
            "case_id": case_id
        }

    def handle_systemic_cluster(self, cluster_key: str, error_signature: str, affected_cases: List[str]) -> Dict[str, Any]:
        """
        Automates multi-customer systemic incident response:
        - Creates Master Incident
        - Bulk-links all affected customer cases
        - Broadcasts initial remediation notice
        """
        title = f"Systemic Gateway Outage: {error_signature} Payment-Order Mismatch"
        description = f"Automated cluster identified {len(affected_cases)} transactions failing with {error_signature}. Triggering bulk remediation."
        incident = db.create_incident(title, description, "HIGH", len(affected_cases), actor=self.name)

        # Bulk link cases
        db.link_cases_to_incident(incident["incident_id"], affected_cases, actor=self.name)

        # Bulk notifications
        db.send_notification(
            "BROADCAST-GROUP",
            "IN_APP_BANNER",
            "Temporary Payment Delay Notice",
            f"We detected a payment gateway synchronization issue. All {len(affected_cases)} affected orders are being automatically reversed within 2 hours.",
            actor=self.name
        )

        return {
            "incident_id": incident["incident_id"],
            "linked_cases_count": len(affected_cases),
            "status": "MASTER_INCIDENT_ORCHESTRATED"
        }

# Global Business Automation instance
business_automation_agent = BusinessAutomationAgent()
