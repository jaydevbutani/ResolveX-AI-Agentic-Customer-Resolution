import os
import sqlite3
import hashlib
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "resolvex_enterprise.db"

def hash_password(password: str) -> str:
    """Secure PBKDF2 password hashing with salt."""
    salt = hashlib.sha256(b"resolvex_enterprise_salt_2026").digest()
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

class SQLiteStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Users table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'OPERATOR',
                created_at TEXT NOT NULL
            )
            """)

            # Sessions table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)

            # Customers table (tenant isolated by user_id)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                account_age_months INTEGER NOT NULL,
                trust_score INTEGER NOT NULL,
                region TEXT NOT NULL,
                status TEXT NOT NULL,
                is_suspicious INTEGER DEFAULT 0,
                PRIMARY KEY (customer_id, user_id)
            )
            """)

            # Transactions table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                order_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                gateway TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                gateway_ref TEXT,
                error_code TEXT,
                refund_id TEXT,
                PRIMARY KEY (transaction_id, user_id)
            )
            """)

            # Orders table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                amount REAL NOT NULL,
                order_status TEXT NOT NULL,
                payment_status TEXT NOT NULL,
                creation_timestamp TEXT NOT NULL,
                fulfilment_status TEXT NOT NULL,
                cancellation_status TEXT NOT NULL,
                provider TEXT DEFAULT 'Generic Merchant',
                item_details TEXT DEFAULT 'General Merchandise',
                PRIMARY KEY (order_id, user_id)
            )
            """)

            # Safe column additions if table already exists
            try:
                cur.execute("ALTER TABLE orders ADD COLUMN provider TEXT DEFAULT 'Generic Merchant'")
            except sqlite3.OperationalError:
                pass
            try:
                cur.execute("ALTER TABLE orders ADD COLUMN item_details TEXT DEFAULT 'General Merchandise'")
            except sqlite3.OperationalError:
                pass

            # Refunds table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS refunds (
                refund_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                initiated_timestamp TEXT NOT NULL,
                expected_completion TEXT NOT NULL,
                bank_reference TEXT NOT NULL,
                initiated_by TEXT NOT NULL,
                PRIMARY KEY (refund_id, user_id)
            )
            """)

            # Support cases table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS support_cases (
                case_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                issue TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                resolution TEXT,
                created_time TEXT NOT NULL,
                PRIMARY KEY (case_id, user_id)
            )
            """)

            # Incidents table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                error_signature TEXT NOT NULL,
                affected_customers INTEGER NOT NULL,
                affected_transactions INTEGER NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                root_pattern TEXT NOT NULL,
                remediation_rule TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (incident_id, user_id)
            )
            """)

            # Chat Sessions table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT DEFAULT 'Customer Inquiry',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)

            # Chat Messages table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                explanation TEXT,
                resolution_data TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)

            conn.commit()

        # Seed default demo accounts if not exist
        self._seed_demo_accounts()

    def _seed_demo_accounts(self):
        demo_accounts = [
            ("USER-DEMO-001", "demo", "demo@resolvex.ai", "STAFF_ARCHITECT"),
            ("USER-CUST-DEMO", "customer_demo", "customer@example.in", "DEMO_CUSTOMER"),
            ("USER-OPS-DEMO", "ops_demo", "ops@resolvex.ai", "DEMO_OPERATIONS"),
            ("USER-EVALUATOR", "evaluator", "evaluator@resolvex.ai", "EVALUATOR")
        ]
        with self.get_connection() as conn:
            cur = conn.cursor()
            for uid, uname, uemail, urole in demo_accounts:
                cur.execute("SELECT user_id FROM users WHERE username = ?", (uname,))
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO users (user_id, username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (uid, uname, uemail, hash_password("demo123" if uname != "evaluator" else "evaluator123"), urole, datetime.now().isoformat())
                    )
            conn.commit()

        # Seed realistic tenant data for all demo accounts
        for uid, _, _, _ in demo_accounts:
            self.seed_user_data(uid)

    def create_guest_session(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Creates an isolated, temporary Guest session with clean state and demo cases."""
        guest_uid = f"GUEST-{uuid.uuid4().hex[:8].upper()}"
        guest_uname = f"guest_{uuid.uuid4().hex[:6]}"
        guest_email = f"{guest_uname}@resolvex.ai"
        sess_id = f"SESS-GUEST-{uuid.uuid4().hex[:10]}"
        now = datetime.now().isoformat()

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (user_id, username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (guest_uid, guest_uname, guest_email, hash_password("guest123"), "GUEST", now)
            )
            cur.execute("INSERT INTO sessions (session_id, user_id, created_at) VALUES (?, ?, ?)", (sess_id, guest_uid, now))
            conn.commit()

        # Seed realistic isolated synthetic data for this guest
        self.seed_user_data(guest_uid)

        user_info = {
            "user_id": guest_uid,
            "username": "Guest Customer",
            "email": guest_email,
            "role": "GUEST",
            "session_id": sess_id,
            "is_guest": True
        }
        return True, "Guest session initialized.", user_info

    def reset_guest_data(self, guest_user_id: str) -> bool:
        """Controlled reset for Guest mode only: deletes and reseeds ONLY the specified guest."""
        if not guest_user_id.startswith("GUEST-"):
            return False
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM customers WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM transactions WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM orders WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM refunds WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM support_cases WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM chat_messages WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM chat_sessions WHERE user_id = ?", (guest_user_id,))
            cur.execute("DELETE FROM audit_logs WHERE user_id = ?", (guest_user_id,))
            conn.commit()
        self.seed_user_data(guest_user_id)
        return True

    def seed_user_data(self, user_id: str):
        """Seeds realistic, extensive synthetic data for a specific user tenant."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Check if user already has data
            cur.execute("SELECT COUNT(*) FROM customers WHERE user_id = ?", (user_id,))
            if cur.fetchone()[0] > 0:
                return

            # 1. Seed Core Demonstration Customers (Scenarios 1-4)
            core_customers = [
                ("CUST-101", user_id, "Rahul Sharma", "rahul.sharma@example.in", "+91-9876543210", 36, 96, "Mumbai, MH", "ACTIVE", 0),
                ("CUST-102", user_id, "Priya Patel", "priya.patel@example.in", "+91-9876543211", 24, 92, "Ahmedabad, GJ", "ACTIVE", 0),
                ("CUST-103", user_id, "Vikram Malhotra", "vikram.m@example.in", "+91-9876543212", 2, 32, "Tor Exit Node 185.220.101.4", "SUSPENDED", 1),
                ("CUST-104", user_id, "Ananya Iyer", "ananya.iyer@example.in", "+91-9876543213", 18, 94, "Bengaluru, KA", "ACTIVE", 0),
                ("CUST-105", user_id, "Rohan Verma", "rohan.v@example.in", "+91-9876543214", 42, 98, "Delhi, DL", "ACTIVE", 0),
            ]
            
            # Expand to 60+ realistic synthetic customers
            regions = ["Delhi, DL", "Bengaluru, KA", "Mumbai, MH", "Hyderabad, TS", "Chennai, TN", "Pune, MH", "Kolkata, WB", "Jaipur, RJ"]
            names = ["Aarav Gupta", "Sneha Rao", "Kabir Sen", "Meera Nair", "Arjun Das", "Diya Kapoor", "Varun Joshi", "Ishita Saxena"]
            
            for i in range(1, 56):
                cid = f"CUST-2{i:02d}"
                cname = f"{names[i % len(names)]} {i}"
                cemail = f"user{i:02d}@megacorp.in"
                cphone = f"+91-980000{i:04d}"
                cregion = regions[i % len(regions)]
                trust = 85 + (i % 14)
                core_customers.append((cid, user_id, cname, cemail, cphone, 12 + (i % 24), trust, cregion, "ACTIVE", 0))

            cur.executemany("""
            INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, core_customers)

            # 2. Seed Core Demonstration Transactions (including 28 Curated Synthetic Cases)
            core_txns = [
                # Existing Core Scenarios 1-4
                ("TXN-8821", user_id, "CUST-101", "ORD-5501", 2499.00, "UPI_AUTO_DEBIT", "RAZORPAY", "2026-10-19T21:14:02", "SUCCESS", "rzp_test_8821a", "PG_TIMEOUT_504", None),
                ("TXN-8822", user_id, "CUST-102", "ORD-5502", 2499.00, "CREDIT_CARD", "RAZORPAY", "2026-10-19T21:20:15", "SUCCESS", "rzp_test_8822b", None, "RF-40192"),
                ("TXN-9901", user_id, "CUST-103", "ORD-5503", 48500.00, "NETBANKING_HDFC", "PAYU", "2026-10-19T21:25:30", "SUCCESS", "payu_test_9901c", "TOR_PROXY_FLAG", None),
                ("TXN-7001", user_id, "CUST-201", "ORD-7001", 1999.00, "UPI_RAZORPAY", "RAZORPAY", "2026-10-19T21:30:00", "SUCCESS", "rzp_test_7001d", "PG_TIMEOUT_504", None),
                
                # Curated Service-Specific Cases (Travel, E-Commerce, Food, Subscriptions)
                ("TXN-8824", user_id, "CUST-101", "ORD-9001", 2499.00, "UPI_GPAY", "RAZORPAY", "2026-10-19T09:00:00", "SUCCESS", "rzp_rb_8824", None, None),
                ("TXN-8829", user_id, "CUST-101", "ORD-9002", 1850.00, "UPI_PHONEPE", "PAYU", "2026-10-20T17:00:00", "SUCCESS", "payu_rb_8829", None, None),
                ("TXN-8830", user_id, "CUST-101", "ORD-9003", 6800.00, "CREDIT_CARD_ICICI", "PAYU", "2026-10-18T11:00:00", "SUCCESS", "payu_mmt_8830", None, None),
                ("TXN-8832", user_id, "CUST-101", "ORD-9004", 4200.00, "NETBANKING_SBI", "RAZORPAY", "2026-10-19T15:00:00", "SUCCESS", "rzp_mmt_8832", None, None),
                ("TXN-8833", user_id, "CUST-101", "ORD-8801", 26990.00, "AMAZON_PAY", "AMAZON_GATEWAY", "2026-10-17T14:00:00", "SUCCESS", "amz_pay_8833", None, None),
                ("TXN-8834", user_id, "CUST-101", "ORD-8802", 14499.00, "CREDIT_CARD_HDFC", "RAZORPAY", "2026-10-18T16:00:00", "SUCCESS", "rzp_amz_8834", None, None),
                ("TXN-8835", user_id, "CUST-101", "ORD-8803", 3999.00, "UPI_PAYTM", "PHONEPE", "2026-10-16T12:00:00", "SUCCESS", "fk_pay_8835", None, None),
                ("TXN-8837", user_id, "CUST-101", "ORD-8805", 749.00, "SWIGGY_PAY", "JUSPAY", "2026-10-20T19:30:00", "SUCCESS", "swg_pay_8837", None, None),
                ("TXN-9101", user_id, "CUST-101", "ORD-9101", 1499.00, "CREDIT_CARD_AUTO", "STRIPE", "2026-10-19T02:00:00", "SUCCESS", "sub_pay_9101", "RENEWAL_AFTER_CANCEL", None),
                ("TXN-9102", user_id, "CUST-101", "ORD-9102", 799.00, "UPI_AUTO_DEBIT", "RAZORPAY", "2026-10-19T02:05:00", "SUCCESS", "sub_pay_9102", "DUPLICATE_SUB_CHARGE", None),
                ("TXN-8828", user_id, "CUST-101", "ORD-8828", 3499.00, "UPI_GPAY", "RAZORPAY", "2026-10-20T14:00:00", "SUCCESS", "rzp_ord_8828", None, None),
            ]

            # Expand to 100+ transactions
            for i in range(1, 101):
                tid = f"TXN-7{i:03d}"
                oid = f"ORD-7{i:03d}"
                cid = f"CUST-2{(i % 55) + 1:02d}"
                amt = 1999.00 if i <= 50 else (499.00 + (i * 25))
                err = "PG_TIMEOUT_504" if i <= 50 else None
                gate = "RAZORPAY" if i <= 60 else "PAYU"
                method = "UPI" if i % 2 == 0 else "CARD"
                core_txns.append((tid, user_id, cid, oid, amt, method, gate, f"2026-10-19T21:{i%60:02d}:00", "SUCCESS", f"gtw_ref_{i:04d}", err, None))

            cur.executemany("""
            INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, core_txns)

            # 3. Seed Core Orders (with Provider and Item Details)
            core_orders = [
                # Existing Core Scenarios 1-4
                ("ORD-5501", user_id, "CUST-101", 2499.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-19T21:14:00", "UNFULFILLED", "NONE", "RedBus", "BLR -> Mumbai Intercity Bus Ticket #RB-10291"),
                ("ORD-5502", user_id, "CUST-102", 2499.00, "FAILED_REFUNDED", "REFUNDED", "2026-10-19T21:20:00", "UNFULFILLED", "PROCESSED", "Generic Merchant", "Electronics Accessory Cart"),
                ("ORD-5503", user_id, "CUST-103", 48500.00, "SECURITY_HOLD", "FLAGGED_REVIEW", "2026-10-19T21:25:00", "HELD", "UNDER_REVIEW", "Amazon", "Apple MacBook Pro M3 (High Risk)"),
                ("ORD-7001", user_id, "CUST-201", 1999.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-19T21:30:00", "UNFULFILLED", "NONE", "Generic Merchant", "Razorpay Payment Gateway Checkout"),

                # Curated Service-Specific Cases
                ("ORD-9001", user_id, "CUST-101", 2499.00, "CANCELLED", "PAID", "2026-10-19T09:00:00", "UNFULFILLED", "CANCELLED_36H_PRIOR", "RedBus", "Bengaluru -> Mumbai Bus #RB-10291 (Eligible Cancellation)"),
                ("ORD-9002", user_id, "CUST-101", 1850.00, "CANCELLED", "PAID", "2026-10-20T17:00:00", "UNFULFILLED", "CANCELLED_2H_PRIOR", "RedBus", "Delhi -> Manali Luxury Bus #RB-10492 (Late Ineligible)"),
                ("ORD-9003", user_id, "CUST-101", 6800.00, "CANCELLED", "PAID", "2026-10-18T11:00:00", "UNFULFILLED", "CANCELLED_FREE_WINDOW", "MakeMyTrip", "Grand Hyatt Goa Resort #MMT-HOTEL-771 (Free Cancellation)"),
                ("ORD-9004", user_id, "CUST-101", 4200.00, "CANCELLED", "PAID", "2026-10-19T15:00:00", "UNFULFILLED", "NON_REFUNDABLE_RATE", "MakeMyTrip", "Taj Santacruz Mumbai #MMT-HOTEL-882 (Non-Refundable Fare)"),
                ("ORD-8801", user_id, "CUST-101", 26990.00, "DELIVERED", "PAID", "2026-10-17T14:00:00", "FULFILLED", "WRONG_ITEM_CLAIMED", "Amazon", "Sony WH-1000XM5 (Delivered Wrong Wired Mouse)"),
                ("ORD-8802", user_id, "CUST-101", 14499.00, "DELIVERED", "PAID", "2026-10-18T16:00:00", "FULFILLED", "DAMAGED_CLAIMED", "Amazon", "LG 27-inch 4K Monitor (Cracked Screen on Arrival)"),
                ("ORD-8803", user_id, "CUST-101", 3999.00, "DELIVERED", "PAID", "2026-10-16T12:00:00", "FULFILLED", "MISSING_ITEM", "Flipkart", "Noise ColorFit Smartwatch 2-Pack (1 Item Missing)"),
                ("ORD-8805", user_id, "CUST-101", 749.00, "DELIVERED", "PAID", "2026-10-20T19:30:00", "FULFILLED", "FOOD_SPILLAGE", "Swiggy", "Meghana Special Biryani (Food Spilled in Transit)"),
                ("ORD-9101", user_id, "CUST-101", 1499.00, "ACTIVE", "PAID", "2026-10-19T02:00:00", "FULFILLED", "CANCELLED_BEFORE_RENEWAL", "Generic Merchant", "Prime Annual Membership (Erroneous Renewal)"),
                ("ORD-9102", user_id, "CUST-101", 799.00, "ACTIVE", "PAID", "2026-10-19T02:05:00", "FULFILLED", "DUPLICATE_CHARGE", "Generic Merchant", "Monthly Cloud Storage Subscription (Duplicate Charge)"),
                ("ORD-8828", user_id, "CUST-101", 3499.00, "CANCELLED", "REFUNDED", "2026-10-20T14:00:00", "UNFULFILLED", "CANCELLED_IMMEDIATE", "Generic Merchant", "Smart Fitness Tracker Band (Auto-Refunded)")
            ]
            for i in range(1, 101):
                oid = f"ORD-7{i:03d}"
                cid = f"CUST-2{(i % 55) + 1:02d}"
                amt = 1999.00 if i <= 50 else (499.00 + (i * 25))
                ostat = "FAILED" if i <= 50 else "DELIVERED"
                pstat = "CAPTURED_NO_ORDER" if i <= 50 else "PAID"
                prov = "Razorpay Gateway" if i <= 50 else "Generic Merchant"
                core_orders.append((oid, user_id, cid, amt, ostat, pstat, f"2026-10-19T21:{i%60:02d}:00", "UNFULFILLED" if i <= 50 else "FULFILLED", "NONE", prov, f"Item SKU #{oid}"))

            cur.executemany("""
            INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, core_orders)

            # 4. Seed Refunds (including RF-40192 for duplicate protection scenario)
            core_refunds = [
                ("RF-40192", user_id, "TXN-8822", 2499.00, "PROCESSING", "2026-10-19T21:22:00", "2026-10-22T18:00:00", "ARN-9928172645-UPI", "Automated Batch")
            ]
            cur.executemany("""
            INSERT OR REPLACE INTO refunds (refund_id, user_id, transaction_id, amount, status, initiated_timestamp, expected_completion, bank_reference, initiated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, core_refunds)

            # 5. Seed Support Cases
            core_cases = [
                ("CASE-101", user_id, "CUST-101", "Money deducted ₹2499 but order failed", "PAYMENT_FAILURE", "HIGH", "OPEN", None, "2026-10-19T21:15:00"),
                ("CASE-102", user_id, "CUST-102", "Second inquiry about refund status for ORD-5502", "REFUND_STATUS", "MEDIUM", "RESOLVED", "ARN-9928172645-UPI provided", "2026-10-19T21:23:00"),
                ("CASE-103", user_id, "CUST-103", "Order held on security verification ₹48,500", "SECURITY_VERIFICATION", "CRITICAL", "ESCALATED_TIER2", "Pending SecOps docket", "2026-10-19T21:26:00")
            ]
            cur.executemany("""
            INSERT OR REPLACE INTO support_cases (case_id, user_id, customer_id, issue, category, severity, status, resolution, created_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, core_cases)

            # 6. Seed Incidents
            core_incidents = [
                ("INC-2026-SYS", user_id, "PG_TIMEOUT_504", 50, 50, "HIGH", "CLUSTER_RESOLVED", "Razorpay callback dropout during peak checkout rush", "Auto-remediation rule synthesized and promoted", "2026-10-19T21:32:00")
            ]
            cur.executemany("""
            INSERT OR REPLACE INTO incidents (incident_id, user_id, error_signature, affected_customers, affected_transactions, severity, status, root_pattern, remediation_rule, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, core_incidents)

            # 7. Seed Initial Audit Logs
            audit_entries = [
                (user_id, "Planner", "PLAN_DECOMPOSE", "2026-10-19T21:14:05", "COMPOSE_DAG", "Formulated 7-stage plan for PG_504", "INITIALIZED"),
                (user_id, "Research", "POLICY_MATCH", "2026-10-19T21:14:06", "MATCH_POL_REF_01", "Retrieved Instant Auto-Refund Policy", "GATHERED"),
                (user_id, "Critic", "PRE_VALIDATE", "2026-10-19T21:14:07", "APPROVE", "5/5 safety checks passed. Low risk authorized.", "VALIDATED"),
            ]
            cur.executemany("""
            INSERT INTO audit_logs (user_id, agent, action, timestamp, decision, result, state_transition)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, audit_entries)

            conn.commit()

    # --- Authentication Methods ---
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if not username or not email or not password:
            return False, "All fields are required.", None
        if len(password) < 4:
            return False, "Password must be at least 4 characters.", None

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
            if cur.fetchone():
                return False, "Username or email already exists.", None

            user_id = f"USER-{uuid.uuid4().hex[:8].upper()}"
            pwd_hash = hash_password(password)
            created_at = datetime.now().isoformat()

            cur.execute(
                "INSERT INTO users (user_id, username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, email, pwd_hash, "OPERATOR", created_at)
            )
            conn.commit()

        # Seed isolated tenant dataset for this new user
        self.seed_user_data(user_id)
        
        user_info = {"user_id": user_id, "username": username, "email": email, "role": "OPERATOR"}
        return True, "Account created successfully.", user_info

    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, username, email, password_hash, role FROM users WHERE username = ? OR email = ?",
                (username_or_email, username_or_email)
            )
            row = cur.fetchone()
            if not row:
                return False, "Invalid credentials.", None

            user_id, username, email, pwd_hash, role = row["user_id"], row["username"], row["email"], row["password_hash"], row["role"]
            if not verify_password(password, pwd_hash):
                return False, "Invalid credentials.", None

            session_id = f"SESS-{uuid.uuid4().hex}"
            cur.execute("INSERT INTO sessions (session_id, user_id, created_at) VALUES (?, ?, ?)", (session_id, user_id, datetime.now().isoformat()))
            conn.commit()

            return True, "Login successful.", {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "session_id": session_id
            }

    # --- Tenant-Isolated Data Access ---
    def get_tenant_customers(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM customers WHERE user_id = ? LIMIT ?", (user_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def get_tenant_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def get_tenant_orders(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY creation_timestamp DESC LIMIT ?", (user_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def get_customer_support_cases(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM support_cases WHERE user_id = ? ORDER BY created_time DESC LIMIT ?", (user_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def find_matching_customer_orders(self, user_id: str, query: str = "") -> List[Dict[str, Any]]:
        """Finds customer orders or bookings that match search query or service name."""
        all_orders = self.get_tenant_orders(user_id, limit=20)
        q_low = query.lower()
        if not q_low or q_low == "all":
            return all_orders
        matches = []
        for o in all_orders:
            prov = (o.get("provider") or "").lower()
            item = (o.get("item_details") or "").lower()
            oid = (o.get("order_id") or "").lower()
            if prov in q_low or q_low in prov or q_low in item or q_low in oid:
                matches.append(o)
            elif ("booking" in q_low or "travel" in q_low) and (prov in ["redbus", "makemytrip"] or "bus" in item or "hotel" in item):
                matches.append(o)
            elif ("refund" in q_low or "cancel" in q_low) and (prov in ["redbus", "makemytrip", "amazon", "swiggy"]):
                matches.append(o)
            elif ("delivery" in q_low or "product" in q_low or "phone" in q_low) and (prov in ["amazon", "flipkart"]):
                matches.append(o)
        return matches if matches else all_orders[:3]

    def get_user_recent_activity(self, user_id: str) -> Dict[str, Any]:
        """Provides consolidated customer context for customer-first homepage."""
        custs = self.get_tenant_customers(user_id, limit=1)
        cust = custs[0] if custs else {"name": "Valued Customer", "customer_id": "CUST-101", "trust_score": 95}
        orders = self.get_tenant_orders(user_id, limit=8)
        refunds = self.get_tenant_refunds(user_id, limit=5)
        cases = self.get_customer_support_cases(user_id, limit=5)

        # Formulate chronological customer events
        timeline = []
        for r in refunds:
            timeline.append({
                "type": "REFUND",
                "title": f"Refund Disbursed: ₹{r['amount']:,.2f}",
                "subtitle": f"ARN: {r['bank_reference']} • Status: {r['status']}",
                "timestamp": r["initiated_timestamp"],
                "badge": "Refunded"
            })
        for c in cases:
            timeline.append({
                "type": "SUPPORT_CASE",
                "title": f"Case #{c['case_id']}: {c['issue'][:45]}",
                "subtitle": f"Status: {c['status']} • Resolution: {c.get('resolution') or 'Under review'}",
                "timestamp": c["created_time"],
                "badge": c["status"]
            })
        for o in orders[:4]:
            timeline.append({
                "type": "ORDER",
                "title": f"{o.get('provider', 'Order')}: {o.get('item_details', o['order_id'])[:45]}",
                "subtitle": f"₹{o['amount']:,.2f} • Payment: {o['payment_status']} • Order: {o['order_status']}",
                "timestamp": o["creation_timestamp"],
                "badge": o["order_status"]
            })

        timeline.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return {
            "customer": cust,
            "recent_orders": orders[:6],
            "recent_refunds": refunds[:4],
            "recent_cases": cases[:4],
            "timeline": timeline[:6]
        }

    def get_tenant_refunds(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM refunds WHERE user_id = ? ORDER BY initiated_timestamp DESC LIMIT ?", (user_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def get_tenant_audit_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM audit_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def record_refund(self, user_id: str, txn_id: str, amount: float, bank_arn: str, refund_id: str):
        with self.get_connection() as conn:
            cur = conn.cursor()
            now = datetime.now().isoformat()
            cur.execute("""
            INSERT OR REPLACE INTO refunds (refund_id, user_id, transaction_id, amount, status, initiated_timestamp, expected_completion, bank_reference, initiated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (refund_id, user_id, txn_id, amount, "SETTLED_REFUND", now, "3-5 business days", bank_arn, "Executor_Agent"))

            cur.execute("""
            UPDATE transactions SET status = 'SETTLED_REFUND', refund_id = ? WHERE transaction_id = ? AND user_id = ?
            """, (refund_id, txn_id, user_id))

            cur.execute("""
            UPDATE orders SET order_status = 'FAILED_REFUNDED', payment_status = 'REFUNDED'
            WHERE user_id = ? AND order_id = (SELECT order_id FROM transactions WHERE transaction_id = ? AND user_id = ?)
            """, (user_id, txn_id, user_id))

            cur.execute("""
            INSERT INTO audit_logs (user_id, agent, action, timestamp, decision, result, state_transition)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, "Executor_Agent", "EXECUTE_REFUND", now, "DISBURSED", f"Refund {refund_id} committed with {bank_arn}", "TRANSACTION_MUTATED"))
            conn.commit()

    # --- Chat Persistence & Conversational Memory ---
    def save_chat_message(self, user_id: str, session_id: str, role: str, content: str, 
                          explanation: Optional[Dict[str, Any]] = None, 
                          resolution_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            now = datetime.now().isoformat()
            
            # Upsert chat session
            cur.execute("""
            INSERT INTO chat_sessions (session_id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET updated_at = excluded.updated_at
            """, (session_id, user_id, content[:40], now, now))

            # Insert message
            msg_id = f"MSG-{uuid.uuid4().hex[:10]}"
            expl_json = json.dumps(explanation) if explanation else None
            res_json = json.dumps(resolution_data) if resolution_data else None

            cur.execute("""
            INSERT INTO chat_messages (message_id, session_id, user_id, role, content, explanation, resolution_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, session_id, user_id, role, content, expl_json, res_json, now))
            conn.commit()

            return {
                "message_id": msg_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "explanation": explanation,
                "resolution_data": resolution_data,
                "timestamp": now
            }

    def get_chat_history(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT message_id, session_id, role, content, explanation, resolution_data, timestamp
            FROM chat_messages
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp ASC
            """, (user_id, session_id))
            rows = cur.fetchall()
            messages = []
            for r in rows:
                m = dict(r)
                if m.get("explanation"):
                    try:
                        m["explanation"] = json.loads(m["explanation"])
                    except Exception:
                        pass
                if m.get("resolution_data"):
                    try:
                        m["resolution_data"] = json.loads(m["resolution_data"])
                    except Exception:
                        pass
                messages.append(m)
            return messages

    def clear_chat_history(self, user_id: str, session_id: str) -> bool:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM chat_messages WHERE user_id = ? AND session_id = ?", (user_id, session_id))
            cur.execute("DELETE FROM chat_sessions WHERE user_id = ? AND session_id = ?", (user_id, session_id))
            conn.commit()
            return True

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id, username, email, role, created_at FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

# Global Singleton
sqlite_store = SQLiteStore()
