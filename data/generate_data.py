import json
from datetime import datetime

def generate_database():
    customers = {
        "CUST-101": {
            "customer_id": "CUST-101",
            "name": "Rahul Sharma",
            "email": "rahul.sharma@example.in",
            "phone": "+91-9876543210",
            "tier": "GOLD",
            "trust_score": 96,
            "is_suspicious": False
        },
        "CUST-102": {
            "customer_id": "CUST-102",
            "name": "Priya Patel",
            "email": "priya.patel@example.in",
            "phone": "+91-9876543211",
            "tier": "SILVER",
            "trust_score": 92,
            "is_suspicious": False
        },
        "CUST-103": {
            "customer_id": "CUST-103",
            "name": "Vikram Malhotra",
            "email": "vikram.m@example.in",
            "phone": "+91-9876543212",
            "tier": "FLAGGED",
            "trust_score": 32,
            "is_suspicious": True
        },
        "CUST-104": {
            "customer_id": "CUST-104",
            "name": "Ananya Iyer",
            "email": "ananya.iyer@example.in",
            "phone": "+91-9876543213",
            "tier": "GOLD",
            "trust_score": 94,
            "is_suspicious": False
        }
    }

    # Add 50 systemic cluster customers
    for i in range(1, 51):
        cid = f"CUST-{200 + i}"
        customers[cid] = {
            "customer_id": cid,
            "name": f"Enterprise User {i:02d}",
            "email": f"user{i:02d}@megacorp.in",
            "phone": f"+91-980000{i:04d}",
            "tier": "STANDARD",
            "trust_score": 90,
            "is_suspicious": False
        }

    transactions = {
        "TXN-8821": {
            "transaction_id": "TXN-8821",
            "customer_id": "CUST-101",
            "amount": 2499.0,
            "currency": "INR",
            "status": "SUCCESS",
            "gateway": "Razorpay",
            "payment_method": "UPI",
            "order_id": "ORD-5501",
            "refund_id": None,
            "error_code": "NONE",
            "timestamp": "2026-10-19T14:30:00",
            "description": "UPI payment received for headphones"
        },
        "TXN-8822": {
            "transaction_id": "TXN-8822",
            "customer_id": "CUST-102",
            "amount": 2499.0,
            "currency": "INR",
            "status": "SUCCESS",
            "gateway": "Razorpay",
            "payment_method": "UPI",
            "order_id": "ORD-5502",
            "refund_id": "RF-40192",
            "error_code": "NONE",
            "timestamp": "2026-10-19T12:00:00",
            "description": "Payment captured, prior refund already queued"
        },
        "TXN-9901": {
            "transaction_id": "TXN-9901",
            "customer_id": "CUST-103",
            "amount": 48500.0,
            "currency": "INR",
            "status": "SUCCESS",
            "gateway": "BillDesk",
            "payment_method": "NetBanking",
            "order_id": "ORD-5503",
            "refund_id": None,
            "error_code": "MISMATCH_DEVICE_IP",
            "timestamp": "2026-10-19T10:15:00",
            "description": "High value payment from untrusted proxy IP"
        },
        "TXN-3301": {
            "transaction_id": "TXN-3301",
            "customer_id": "CUST-104",
            "amount": 1499.0,
            "currency": "INR",
            "status": "SUCCESS",
            "gateway": "Stripe",
            "payment_method": "CreditCard",
            "order_id": "SUB-101",
            "refund_id": None,
            "error_code": "NONE",
            "timestamp": "2026-10-19T02:00:00",
            "description": "Subscription automated charge"
        }
    }

    # Add 50 systemic cluster transactions
    for i in range(1, 51):
        tx_id = f"TXN-70{i:02d}"
        ord_id = f"ORD-70{i:02d}"
        cid = f"CUST-{200 + i}"
        transactions[tx_id] = {
            "transaction_id": tx_id,
            "customer_id": cid,
            "amount": 1999.0,
            "currency": "INR",
            "status": "SUCCESS",
            "gateway": "Razorpay",
            "payment_method": "UPI",
            "order_id": ord_id,
            "refund_id": None,
            "error_code": "PG_TIMEOUT_504",
            "timestamp": f"2026-10-19T15:{10 + (i % 15):02d}:00",
            "description": "Flash Sale Checkout Payment Captured"
        }

    orders = {
        "ORD-5501": {
            "order_id": "ORD-5501",
            "customer_id": "CUST-101",
            "transaction_id": "TXN-8821",
            "items": [{"name": "Acoustic Pro Wireless Earbuds", "qty": 1, "price": 2499.0}],
            "total_amount": 2499.0,
            "status": "FAILED",
            "failure_reason": "INVENTORY_RESERVATION_TIMEOUT",
            "created_at": "2026-10-19T14:30:05",
            "updated_at": "2026-10-19T14:30:05"
        },
        "ORD-5502": {
            "order_id": "ORD-5502",
            "customer_id": "CUST-102",
            "transaction_id": "TXN-8822",
            "items": [{"name": "Smart Fitness Band 7", "qty": 1, "price": 2499.0}],
            "total_amount": 2499.0,
            "status": "FAILED",
            "failure_reason": "GATEWAY_CALLBACK_TIMEOUT",
            "created_at": "2026-10-19T12:00:05",
            "updated_at": "2026-10-19T12:00:05"
        },
        "ORD-5503": {
            "order_id": "ORD-5503",
            "customer_id": "CUST-103",
            "transaction_id": "TXN-9901",
            "items": [{"name": "4K Ultra HD Gaming Monitor 144Hz", "qty": 1, "price": 48500.0}],
            "total_amount": 48500.0,
            "status": "FAILED",
            "failure_reason": "MANUAL_HOLD_DEVICE_SUSPICIOUS",
            "created_at": "2026-10-19T10:15:10",
            "updated_at": "2026-10-19T10:15:10"
        }
    }

    # Add 50 systemic cluster orders
    for i in range(1, 51):
        ord_id = f"ORD-70{i:02d}"
        tx_id = f"TXN-70{i:02d}"
        cid = f"CUST-{200 + i}"
        orders[ord_id] = {
            "order_id": ord_id,
            "customer_id": cid,
            "transaction_id": tx_id,
            "items": [{"name": "Festive Super Sale Bundle", "qty": 1, "price": 1999.0}],
            "total_amount": 1999.0,
            "status": "FAILED",
            "failure_reason": "PG_GATEWAY_TIMEOUT",
            "created_at": f"2026-10-19T15:{10 + (i % 15):02d}:05",
            "updated_at": f"2026-10-19T15:{10 + (i % 15):02d}:05"
        }

    refunds = {
        "RF-40192": {
            "refund_id": "RF-40192",
            "transaction_id": "TXN-8822",
            "order_id": "ORD-5502",
            "customer_id": "CUST-102",
            "amount": 2499.0,
            "currency": "INR",
            "status": "PROCESSING",
            "arn": "ARN-9928172645-UPI",
            "gateway": "Razorpay",
            "initiated_at": "2026-10-19T12:05:00",
            "estimated_credit": "2026-10-20T12:05:00",
            "notes": "Initiated prior to inquiry; credit expected in bank within 24h"
        }
    }

    subscriptions = {
        "SUB-101": {
            "subscription_id": "SUB-101",
            "customer_id": "CUST-104",
            "plan_name": "Pro Annual Plan",
            "amount": 1499.0,
            "status": "CANCELLED",
            "cancelled_at": "2026-10-18T10:00:00",
            "charged_at": "2026-10-19T02:00:00",
            "last_transaction_id": "TXN-3301"
        }
    }

    cases = {
        "CASE-001": {
            "case_id": "CASE-001",
            "customer_id": "CUST-101",
            "channel": "WEB_COMPLAINT",
            "issue_type": "MONEY_DEDUCTED_ORDER_FAILED",
            "description": "₹2,499 was deducted but my order failed.",
            "status": "OPEN",
            "priority": "HIGH",
            "resolution_state": "UNRESOLVED",
            "parent_incident_id": None,
            "created_at": "2026-10-19T14:32:00",
            "closed_at": None,
            "resolution_summary": None
        }
    }

    # Pre-populate initial 50 systemic cases
    for i in range(1, 51):
        case_id = f"CASE-SYS-{i:03d}"
        cid = f"CUST-{200 + i}"
        cases[case_id] = {
            "case_id": case_id,
            "customer_id": cid,
            "channel": "AUTO_INGEST",
            "issue_type": "PAYMENT_CAPTURE_WITHOUT_ORDER",
            "description": f"₹1,999 debited on Razorpay, order ORD-70{i:02d} dropped with PG_TIMEOUT_504.",
            "status": "OPEN",
            "priority": "HIGH",
            "resolution_state": "PENDING_CLUSTER_ANALYSIS",
            "parent_incident_id": None,
            "created_at": f"2026-10-19T15:{12 + (i % 15):02d}:00",
            "closed_at": None,
            "resolution_summary": None
        }

    incidents = {}
    notifications = []
    audit_logs = [
        {
            "timestamp": "2026-10-19T14:30:00",
            "actor": "SYSTEM_SEEDS",
            "action": "DATABASE_INITIALIZATION",
            "details": "Synthetic enterprise database primed for ResolveX AI testing."
        }
    ]

    db_state = {
        "customers": customers,
        "transactions": transactions,
        "orders": orders,
        "refunds": refunds,
        "subscriptions": subscriptions,
        "cases": cases,
        "incidents": incidents,
        "notifications": notifications,
        "audit_logs": audit_logs
    }

    with open("data/synthetic_db.json", "w", encoding="utf-8") as f:
        json.dump(db_state, f, indent=2)

    # Also keep a clean template copy so we can instantly reset the database anytime!
    with open("data/synthetic_db_template.json", "w", encoding="utf-8") as f:
        json.dump(db_state, f, indent=2)

    print("Synthetic database generated successfully.")

if __name__ == "__main__":
    generate_database()
