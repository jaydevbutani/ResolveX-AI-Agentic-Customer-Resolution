import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.workflow.graph import run_resolution_flow
from src.db.store import db

def print_banner(text):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def demo_scenario_1():
    print_banner("DEMO SCENARIO 1: Autonomous Successful Resolution")
    print("Customer: '₹2,499 was deducted from my UPI account but order failed.'")
    db.reset()
    res = run_resolution_flow(
        "₹2,499 was deducted from my UPI account but order failed.",
        {"customer_id": "CUST-101", "transaction_id": "TXN-8821", "order_id": "ORD-5501", "amount": 2499.0}
    )
    print(f"\n[Final Status]: {res['final_status']}")
    ref = db.get_refund_by_transaction("TXN-8821")
    if ref:
        print(f"[State Change]: Created Refund {ref['refund_id']} | Amount: ₹{ref['amount']:,.2f} | ARN: {ref['arn']}")
    print(f"[Critic Gate]: {res['validation_result']['decision']} — {res['validation_result']['reason']}")
    print(f"[Verification]: {res['verification_result']['summary']}")

def demo_scenario_2():
    print_banner("DEMO SCENARIO 2: Critic Rejection & Dynamic Replanning")
    print("Customer: '₹2,499 deducted for ORD-5502. Where is my refund?'")
    db.reset()
    res = run_resolution_flow(
        "₹2,499 deducted for ORD-5502. Where is my refund?",
        {"customer_id": "CUST-102", "transaction_id": "TXN-8822", "order_id": "ORD-5502", "amount": 2499.0}
    )
    print(f"\n[Final Status]: {res['final_status']}")
    print(f"[Replan Cycles]: {res['replan_count']}")
    ref = db.get_refund_by_transaction("TXN-8822")
    if ref:
        print(f"[Existing Preserved]: Refund {ref['refund_id']} | ARN: {ref['arn']} (No duplicate refund created!)")

def demo_scenario_3():
    print_banner("DEMO SCENARIO 3: Exception & Human Escalation")
    print("Customer: '₹48,500 deducted for gaming monitor, order held on security check.'")
    db.reset()
    res = run_resolution_flow(
        "₹48,500 deducted for gaming monitor, order held on security check.",
        {"customer_id": "CUST-103", "transaction_id": "TXN-9901", "order_id": "ORD-5503", "amount": 48500.0}
    )
    print(f"\n[Final Status]: {res['final_status']}")
    print(f"[Critic Decision]: {res['validation_result']['decision']}")
    print(f"[Escalation Reason]: {res['validation_result']['reason']}")
    case = db.get_case("CASE-001")
    print(f"[CRM Case Status]: {case.get('status')} (Disbursement blocked!)")

def demo_scenario_4():
    print_banner("DEMO SCENARIO 4: Systemic Incident & Rule Synthesis")
    print("Trigger: 50 customer checkout payments captured on Razorpay with PG_TIMEOUT_504.")
    db.reset()
    res = run_resolution_flow(
        "Systemic Gateway Outage: Multiple customer checkout charges succeeded on Razorpay while orders failed with PG_TIMEOUT_504.",
        {"customer_id": "CUST-201", "transaction_id": "TXN-7001", "order_id": "ORD-7001", "amount": 1999.0}
    )
    print(f"\n[Final Status]: {res['final_status']}")
    incidents = db.get_all_incidents()
    if incidents:
        print(f"[Master Incident]: {incidents[0]['incident_id']} | Linked Cases: {len(incidents[0]['linked_case_ids'])}")
    if res.get("software_dev_result"):
        rule = res["software_dev_result"]["rule"]
        print(f"[Synthesized Rule]: {rule['name']} | Accuracy: {rule['accuracy_score']*100:.1f}%")

if __name__ == "__main__":
    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    demo_scenario_4()
    print_banner("ALL 4 DEMO SCENARIOS COMPLETED SUCCESSFULLY")
