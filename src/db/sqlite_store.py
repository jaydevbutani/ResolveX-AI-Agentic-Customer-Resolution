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
            ("USER-JAYDEV", "jaydev", "jaydev@resolvex.ai", "DEMO_CUSTOMER"),
            ("USER-RAJVI", "rajvi", "rajvi@resolvex.ai", "DEMO_CUSTOMER"),
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

    def delete_session(self, session_id: str) -> bool:
        """Destroys active server session upon logout."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return True

    def reseed_tenant(self, user_id: str) -> bool:
        """Completely purges and reseeds tenant data for a specific user ID."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM customers WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM refunds WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM support_cases WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM audit_logs WHERE user_id = ?", (user_id,))
            conn.commit()
        self.seed_user_data(user_id)
        return True

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
        """Seeds realistic, extensive synthetic data strictly isolated for a specific user tenant."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # Check if user already has data
            cur.execute("SELECT COUNT(*) FROM customers WHERE user_id = ?", (user_id,))
            if cur.fetchone()[0] > 0:
                return

            if user_id in ["USER-JAYDEV", "USER-JD"] or "jaydev" in user_id.lower():
                self._seed_jaydev_data(cur, user_id)
            elif user_id in ["USER-RAJVI", "USER-RV"] or "rajvi" in user_id.lower():
                self._seed_rajvi_data(cur, user_id)
            elif user_id.startswith("GUEST-"):
                self._seed_guest_data(cur, user_id)
            elif user_id == "USER-CUST-DEMO" or "cust-demo" in user_id.lower():
                self._seed_rahul_data(cur, user_id)
            elif user_id in ["USER-DEMO-001", "USER-EVALUATOR", "USER-OPS-DEMO"]:
                self._seed_evaluator_data(cur, user_id)
            else:
                self._seed_dynamic_user_data(cur, user_id)

            conn.commit()

    def _seed_jaydev_data(self, cur, user_id: str):
        """Seeds realistic synthetic profile and orders unique to Jaydev Butani."""
        # 1. Customer Profiles
        custs = [
            ("CUST-JAYDEV", user_id, "Jaydev Butani", "jaydev@resolvex.ai", "+91-9988776655", 28, 98, "Ahmedabad, GJ", "ACTIVE", 0),
            ("CUST-JD-02", user_id, "Ananya Butani", "ananya.b@resolvex.ai", "+91-9988776656", 14, 94, "Mumbai, MH", "ACTIVE", 0)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, custs)

        # 2. Transactions
        txns = [
            ("TXN-JD-101", user_id, "CUST-JAYDEV", "ORD-JD-101", 5400.00, "CREDIT_CARD_HDFC", "PAYU", "2026-10-18T10:30:00", "SUCCESS", "gtw_jd_101", None, None),
            ("TXN-JD-102", user_id, "CUST-JAYDEV", "ORD-JD-102", 64999.00, "NETBANKING_ICICI", "RAZORPAY", "2026-10-17T14:20:00", "SUCCESS", "gtw_jd_102", None, None),
            ("TXN-JD-103", user_id, "CUST-JAYDEV", "ORD-JD-103", 1299.00, "UPI_GPAY", "JUSPAY", "2026-10-20T20:15:00", "SUCCESS", "gtw_jd_103", None, None),
            ("TXN-JD-104", user_id, "CUST-JAYDEV", "ORD-JD-104", 1890.00, "UPI_PHONEPE", "RAZORPAY", "2026-10-19T08:00:00", "SETTLED_REFUND", "gtw_jd_104", None, "RF-JD-104"),
            ("TXN-JD-105", user_id, "CUST-JAYDEV", "ORD-JD-105", 13999.00, "CREDIT_CARD_SBI", "AMAZON_PAY", "2026-10-15T11:00:00", "SUCCESS", "gtw_jd_105", None, None),
            ("TXN-JD-106", user_id, "CUST-JAYDEV", "ORD-JD-106", 12500.00, "CREDIT_CARD_HDFC", "PAYU", "2026-10-19T14:00:00", "SUCCESS", "gtw_jd_106", None, None),
            ("TXN-JD-107", user_id, "CUST-JAYDEV", "ORD-JD-107", 680.00, "UPI_PAYTM", "JUSPAY", "2026-10-20T16:00:00", "SUCCESS", "gtw_jd_107", None, None),
            ("TXN-JD-108", user_id, "CUST-JAYDEV", "ORD-JD-108", 1000.00, "UPI_AUTO_DEBIT", "RAZORPAY", "2026-10-20T12:00:00", "SUCCESS", "gtw_jd_108", "PG_TIMEOUT_504", None),
            ("TXN-JD-109", user_id, "CUST-JAYDEV", "ORD-JD-109", 7788.00, "CARD_RECURRING", "STRIPE", "2026-10-01T00:00:00", "SUCCESS", "gtw_jd_109", None, None),
            ("TXN-JD-110", user_id, "CUST-JAYDEV", "ORD-JD-110", 14148.00, "NETBANKING_HDFC", "RAZORPAY", "2026-10-19T18:45:00", "SUCCESS", "gtw_jd_110", "PG_TIMEOUT_504", None),
            ("TXN-JD-111", user_id, "CUST-JAYDEV", "ORD-JD-111", 2499.00, "UPI_GPAY", "RAZORPAY", "2026-10-16T09:30:00", "SUCCESS", "gtw_jd_111", None, None),
            ("TXN-JD-112", user_id, "CUST-JAYDEV", "ORD-JD-112", 209900.00, "NETBANKING_HDFC", "PAYU", "2026-10-20T22:00:00", "SUCCESS", "gtw_jd_112", "TOR_PROXY_FLAG", None)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, txns)

        # 3. Orders
        ords = [
            ("ORD-JD-101", user_id, "CUST-JAYDEV", 5400.00, "DELIVERED", "PAID", "2026-10-18T10:30:00", "FULFILLED", "NONE", "MakeMyTrip", "Mumbai -> Goa Flight Ticket #MMT-FL-902"),
            ("ORD-JD-102", user_id, "CUST-JAYDEV", 64999.00, "DELIVERED", "PAID", "2026-10-17T14:20:00", "FULFILLED", "NONE", "Flipkart", "OnePlus 12 Emerald 512GB Smartphone"),
            ("ORD-JD-103", user_id, "CUST-JAYDEV", 1299.00, "DELIVERED", "PAID", "2026-10-20T20:15:00", "FULFILLED", "NONE", "Swiggy", "Woodfired Italian Pizza & Pasta Gourmet Combo"),
            ("ORD-JD-104", user_id, "CUST-JAYDEV", 1890.00, "CANCELLED", "REFUNDED", "2026-10-19T08:00:00", "UNFULFILLED", "CANCELLED_48H_PRIOR", "RedBus", "Ahmedabad -> Mumbai Volvo Sleeper #RB-AHM-44"),
            ("ORD-JD-105", user_id, "CUST-JAYDEV", 13999.00, "DELIVERED", "PAID", "2026-10-15T11:00:00", "FULFILLED", "NONE", "Amazon", "Amazon Kindle Paperwhite 11th Gen (16 GB)"),
            ("ORD-JD-106", user_id, "CUST-JAYDEV", 12500.00, "CANCELLED", "PAID", "2026-10-19T14:00:00", "UNFULFILLED", "CANCELLED_FREE_WINDOW", "MakeMyTrip", "Taj Resort & Convention Centre Goa #MMT-HTL-109"),
            ("ORD-JD-107", user_id, "CUST-JAYDEV", 680.00, "DELIVERED", "PAID", "2026-10-20T16:00:00", "FULFILLED", "NONE", "Swiggy", "Blue Tokai Specialty Coffee & Croissant"),
            ("ORD-JD-108", user_id, "CUST-JAYDEV", 1000.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-20T12:00:00", "UNFULFILLED", "NONE", "Generic Merchant", "Fastag Toll Auto-Recharge #RZP-FST-882"),
            ("ORD-JD-109", user_id, "CUST-JAYDEV", 7788.00, "ACTIVE", "PAID", "2026-10-01T00:00:00", "FULFILLED", "NONE", "Generic Merchant", "Netflix Premium 4K Annual Membership"),
            ("ORD-JD-110", user_id, "CUST-JAYDEV", 14148.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-19T18:45:00", "UNFULFILLED", "NONE", "Generic Merchant", "JioFiber 1Gbps Gigabit Ultra Annual Plan"),
            ("ORD-JD-111", user_id, "CUST-JAYDEV", 2499.00, "DELIVERED", "PAID", "2026-10-16T09:30:00", "FULFILLED", "NONE", "Urban Company", "Urban Company Full Home Deep Cleaning"),
            ("ORD-JD-112", user_id, "CUST-JAYDEV", 209900.00, "SECURITY_HOLD", "FLAGGED_REVIEW", "2026-10-20T22:00:00", "HELD", "UNDER_REVIEW", "Amazon", "Apple Mac Studio M2 Ultra (High Value)")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ords)

        # 4. Refunds
        refs = [
            ("RF-JD-104", user_id, "TXN-JD-104", 1890.00, "SETTLED_REFUND", "2026-10-19T08:15:00", "2026-10-21T18:00:00", "ARN-JD-98214-UPI", "Automated Batch")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO refunds (refund_id, user_id, transaction_id, amount, status, initiated_timestamp, expected_completion, bank_reference, initiated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, refs)

        # 5. Cases
        cases = [
            ("CASE-JD-01", user_id, "CUST-JAYDEV", "JioFiber Annual Recharge deducted ₹14,148 but account uncredited", "PAYMENT_FAILURE", "HIGH", "OPEN", None, "2026-10-19T18:50:00"),
            ("CASE-JD-02", user_id, "CUST-JAYDEV", "RedBus Ahmedabad-Mumbai Volvo ticket cancellation refund processed", "REFUND_STATUS", "MEDIUM", "RESOLVED", "ARN-JD-98214-UPI provided", "2026-10-19T08:20:00")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO support_cases (case_id, user_id, customer_id, issue, category, severity, status, resolution, created_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cases)

    def _seed_rajvi_data(self, cur, user_id: str):
        """Seeds realistic synthetic profile and orders unique to Rajvi Patel."""
        # 1. Customer Profiles
        custs = [
            ("CUST-RAJVI", user_id, "Rajvi Patel", "rajvi@resolvex.ai", "+91-9876543210", 22, 97, "Bengaluru, KA", "ACTIVE", 0),
            ("CUST-RV-02", user_id, "Devina Patel", "devina.p@resolvex.ai", "+91-9876543211", 12, 92, "Mumbai, MH", "ACTIVE", 0)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, custs)

        # 2. Transactions
        txns = [
            ("TXN-RV-101", user_id, "CUST-RAJVI", "ORD-RV-101", 3450.00, "UPI_GPAY", "RAZORPAY", "2026-10-18T11:20:00", "SUCCESS", "gtw_rv_101", None, None),
            ("TXN-RV-102", user_id, "CUST-RAJVI", "ORD-RV-102", 4990.00, "CREDIT_CARD_HDFC", "PAYU", "2026-10-17T16:45:00", "SETTLED_REFUND", "gtw_rv_102", None, "RF-RV-102"),
            ("TXN-RV-103", user_id, "CUST-RAJVI", "ORD-RV-103", 24900.00, "CREDIT_CARD_ICICI", "RAZORPAY", "2026-10-16T14:10:00", "SUCCESS", "gtw_rv_103", None, None),
            ("TXN-RV-104", user_id, "CUST-RAJVI", "ORD-RV-104", 18500.00, "NETBANKING_SBI", "PAYU", "2026-10-19T09:30:00", "SUCCESS", "gtw_rv_104", None, None),
            ("TXN-RV-105", user_id, "CUST-RAJVI", "ORD-RV-105", 850.00, "UPI_PHONEPE", "JUSPAY", "2026-10-20T19:40:00", "SUCCESS", "gtw_rv_105", None, None),
            ("TXN-RV-106", user_id, "CUST-RAJVI", "ORD-RV-106", 2800.00, "UPI_PAYTM", "RAZORPAY", "2026-10-20T14:00:00", "SUCCESS", "gtw_rv_106", None, None),
            ("TXN-RV-107", user_id, "CUST-RAJVI", "ORD-RV-107", 1240.00, "UPI_GPAY", "JUSPAY", "2026-10-20T17:15:00", "SUCCESS", "gtw_rv_107", None, None),
            ("TXN-RV-108", user_id, "CUST-RAJVI", "ORD-RV-108", 3200.00, "UPI_PHONEPE", "RAZORPAY", "2026-10-20T12:30:00", "SUCCESS", "gtw_rv_108", "PG_TIMEOUT_504", None),
            ("TXN-RV-109", user_id, "CUST-RAJVI", "ORD-RV-109", 16999.00, "CARD_RECURRING", "STRIPE", "2026-10-01T00:00:00", "SUCCESS", "gtw_rv_109", None, None),
            ("TXN-RV-110", user_id, "CUST-RAJVI", "ORD-RV-110", 45900.00, "NETBANKING_HDFC", "PAYU", "2026-10-20T21:00:00", "SUCCESS", "gtw_rv_110", "HIGH_VALUE_HOLD", None)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, txns)

        # 3. Orders
        ords = [
            ("ORD-RV-101", user_id, "CUST-RAJVI", 3450.00, "DELIVERED", "PAID", "2026-10-18T11:20:00", "FULFILLED", "NONE", "Nykaa", "Nykaa Luxury Korean Skincare & Glow Set"),
            ("ORD-RV-102", user_id, "CUST-RAJVI", 4990.00, "CANCELLED", "REFUNDED", "2026-10-17T16:45:00", "UNFULFILLED", "CANCELLED_FREE_WINDOW", "Zara", "Zara Summer Floral Maxi Dress (Size M)"),
            ("ORD-RV-103", user_id, "CUST-RAJVI", 24900.00, "DELIVERED", "PAID", "2026-10-16T14:10:00", "FULFILLED", "NONE", "Croma", "Apple AirPods Pro 2nd Gen with MagSafe USB-C"),
            ("ORD-RV-104", user_id, "CUST-RAJVI", 18500.00, "CONFIRMED", "PAID", "2026-10-19T09:30:00", "FULFILLED", "NONE", "MakeMyTrip", "Udaipur Heritage Palace Resort 2N Weekend Stay"),
            ("ORD-RV-105", user_id, "CUST-RAJVI", 850.00, "DELIVERED", "PAID", "2026-10-20T19:40:00", "FULFILLED", "NONE", "Swiggy", "Artisan Bakery Sourdough Loaf & Gourmet Tarts"),
            ("ORD-RV-106", user_id, "CUST-RAJVI", 2800.00, "DELIVERED", "PAID", "2026-10-20T14:00:00", "FULFILLED", "NONE", "Urban Company", "Urban Company Full Salon & Aroma Spa Package"),
            ("ORD-RV-107", user_id, "CUST-RAJVI", 1240.00, "DELIVERED", "PAID", "2026-10-20T17:15:00", "FULFILLED", "NONE", "Blinkit", "Organic Hass Avocados & Hydroponic Berries"),
            ("ORD-RV-108", user_id, "CUST-RAJVI", 3200.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-20T12:30:00", "UNFULFILLED", "NONE", "FabIndia", "FabIndia Handcrafted Mulberry Silk Stole"),
            ("ORD-RV-109", user_id, "CUST-RAJVI", 16999.00, "ACTIVE", "PAID", "2026-10-01T00:00:00", "FULFILLED", "NONE", "Cult.fit", "Cult.fit Elite Pass Unlimited 12-Month Access"),
            ("ORD-RV-110", user_id, "CUST-RAJVI", 45900.00, "SECURITY_HOLD", "FLAGGED_REVIEW", "2026-10-20T21:00:00", "HELD", "UNDER_REVIEW", "Dyson India", "Dyson Airwrap Multi-Styler Complete Long Nickel/Copper")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ords)

        # 4. Refunds
        refs = [
            ("RF-RV-102", user_id, "TXN-RV-102", 4990.00, "SETTLED_REFUND", "2026-10-17T17:00:00", "2026-10-19T14:00:00", "ARN-RV-88192-HDFC", "Automated Policy Refund")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO refunds (refund_id, user_id, transaction_id, amount, status, initiated_timestamp, expected_completion, bank_reference, initiated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, refs)

        # 5. Cases
        cases = [
            ("CASE-RV-01", user_id, "CUST-RAJVI", "FabIndia Silk Stole payment debited ₹3,200 but checkout crashed", "PAYMENT_FAILURE", "HIGH", "OPEN", None, "2026-10-20T12:35:00"),
            ("CASE-RV-02", user_id, "CUST-RAJVI", "Zara Summer Dress cancellation refund status check", "REFUND_STATUS", "LOW", "RESOLVED", "ARN-RV-88192-HDFC confirmed credited", "2026-10-17T17:05:00")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO support_cases (case_id, user_id, customer_id, issue, category, severity, status, resolution, created_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cases)

    def _seed_guest_data(self, cur, user_id: str):
        """Seeds realistic synthetic profile and orders unique to temporary Guest sessions."""
        custs = [
            ("CUST-GUEST", user_id, "Guest Customer", f"guest_{user_id[-6:]}@resolvex.ai", "+91-9000000000", 1, 90, "Delhi, DL", "ACTIVE", 0)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, custs)

        txns = [
            ("TXN-GST-101", user_id, "CUST-GUEST", "ORD-GST-101", 1250.00, "UPI_GPAY", "RAZORPAY", "2026-10-20T11:00:00", "SUCCESS", "gtw_gst_101", None, None),
            ("TXN-GST-102", user_id, "CUST-GUEST", "ORD-GST-102", 420.00, "UPI_PAYTM", "JUSPAY", "2026-10-20T13:30:00", "SUCCESS", "gtw_gst_102", None, None),
            ("TXN-GST-103", user_id, "CUST-GUEST", "ORD-GST-103", 4499.00, "CREDIT_CARD", "AMAZON_PAY", "2026-10-18T15:00:00", "SUCCESS", "gtw_gst_103", None, None),
            ("TXN-GST-104", user_id, "CUST-GUEST", "ORD-GST-104", 3200.00, "NETBANKING", "PAYU", "2026-10-19T10:00:00", "SUCCESS", "gtw_gst_104", None, None),
            ("TXN-GST-105", user_id, "CUST-GUEST", "ORD-GST-105", 650.00, "UPI", "RAZORPAY", "2026-10-20T17:00:00", "SUCCESS", "gtw_gst_105", "PG_TIMEOUT_504", None)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, txns)

        ords = [
            ("ORD-GST-101", user_id, "CUST-GUEST", 1250.00, "DELIVERED", "PAID", "2026-10-20T11:00:00", "FULFILLED", "NONE", "RedBus", "Pune -> Mumbai Shivneri Volvo #RB-GST-101"),
            ("ORD-GST-102", user_id, "CUST-GUEST", 420.00, "DELIVERED", "PAID", "2026-10-20T13:30:00", "FULFILLED", "NONE", "Swiggy", "Fresh Green Salad & Organic Smoothie Bowl"),
            ("ORD-GST-103", user_id, "CUST-GUEST", 4499.00, "DELIVERED", "PAID", "2026-10-18T15:00:00", "FULFILLED", "NONE", "Amazon", "Amazon Echo Dot 5th Gen Smart Speaker"),
            ("ORD-GST-104", user_id, "CUST-GUEST", 3200.00, "CANCELLED", "PAID", "2026-10-19T10:00:00", "UNFULFILLED", "CANCELLED_FREE_WINDOW", "MakeMyTrip", "Pune Business Hotel Executive Suite"),
            ("ORD-GST-105", user_id, "CUST-GUEST", 650.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-20T17:00:00", "UNFULFILLED", "NONE", "Generic Merchant", "Tata Play DTH Monthly Mega Entertainment Pack")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ords)

        cases = [
            ("CASE-GST-01", user_id, "CUST-GUEST", "Inquiry regarding MakeMyTrip hotel cancellation refund", "REFUND_STATUS", "MEDIUM", "OPEN", None, "2026-10-19T10:15:00")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO support_cases (case_id, user_id, customer_id, issue, category, severity, status, resolution, created_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cases)

    def _seed_rahul_data(self, cur, user_id: str):
        """Seeds 30 curated synthetic cases across Travel, E-Commerce, Food, Payments, Subscriptions, Digital, Utility, High-Risk for Rahul Sharma."""
        custs = [
            ("CUST-101", user_id, "Rahul Sharma", "rahul.sharma@example.in", "+91-9876543210", 36, 96, "Mumbai, MH", "ACTIVE", 0),
            ("CUST-102", user_id, "Priya Patel", "priya.patel@example.in", "+91-9876543211", 24, 92, "Ahmedabad, GJ", "ACTIVE", 0),
            ("CUST-103", user_id, "Vikram Malhotra", "vikram.m@example.in", "+91-9876543212", 2, 32, "Tor Exit Node 185.220.101.4", "SUSPENDED", 1)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, custs)

        txns = [
            # Travel Cases
            ("TXN-8821", user_id, "CUST-101", "ORD-5501", 2499.00, "UPI_AUTO_DEBIT", "RAZORPAY", "2026-10-19T21:14:02", "SUCCESS", "rzp_test_8821a", "PG_TIMEOUT_504", None),
            ("TXN-8824", user_id, "CUST-101", "ORD-9001", 2499.00, "UPI_GPAY", "RAZORPAY", "2026-10-19T09:00:00", "SUCCESS", "rzp_rb_8824", None, None),
            ("TXN-8829", user_id, "CUST-101", "ORD-9002", 1850.00, "UPI_PHONEPE", "PAYU", "2026-10-20T17:00:00", "SUCCESS", "payu_rb_8829", None, None),
            ("TXN-8830", user_id, "CUST-101", "ORD-9003", 6800.00, "CREDIT_CARD_ICICI", "PAYU", "2026-10-18T11:00:00", "SUCCESS", "payu_mmt_8830", None, None),
            ("TXN-8832", user_id, "CUST-101", "ORD-9004", 4200.00, "NETBANKING_SBI", "RAZORPAY", "2026-10-19T15:00:00", "SUCCESS", "rzp_mmt_8832", None, None),
            ("TXN-8838", user_id, "CUST-101", "ORD-9005", 5890.00, "CREDIT_CARD_HDFC", "PAYU", "2026-10-17T08:00:00", "SUCCESS", "payu_indigo_8838", None, None),
            ("TXN-8839", user_id, "CUST-101", "ORD-9006", 18400.00, "NETBANKING_HDFC", "PAYU", "2026-10-16T19:00:00", "SUCCESS", "payu_airindia_8839", None, None),

            # E-Commerce Cases
            ("TXN-8833", user_id, "CUST-101", "ORD-8801", 26990.00, "AMAZON_PAY", "AMAZON_GATEWAY", "2026-10-17T14:00:00", "SUCCESS", "amz_pay_8833", None, None),
            ("TXN-8834", user_id, "CUST-101", "ORD-8802", 14499.00, "CREDIT_CARD_HDFC", "RAZORPAY", "2026-10-18T16:00:00", "SUCCESS", "rzp_amz_8834", None, None),
            ("TXN-8835", user_id, "CUST-101", "ORD-8803", 3999.00, "UPI_PAYTM", "PHONEPE", "2026-10-16T12:00:00", "SUCCESS", "fk_pay_8835", None, None),
            ("TXN-8840", user_id, "CUST-101", "ORD-8804", 59900.00, "CREDIT_CARD_ICICI", "AMAZON_PAY", "2026-10-15T18:00:00", "SUCCESS", "amz_pay_8840", None, None),
            ("TXN-8841", user_id, "CUST-101", "ORD-8806", 2899.00, "UPI_GPAY", "PHONEPE", "2026-09-15T11:00:00", "SUCCESS", "fk_pay_8841", None, None),
            ("TXN-8842", user_id, "CUST-101", "ORD-8807", 34999.00, "CREDIT_CARD_HDFC", "AMAZON_PAY", "2026-10-18T20:00:00", "SUCCESS", "amz_pay_8842", None, None),

            # Food Delivery Cases
            ("TXN-8837", user_id, "CUST-101", "ORD-8805", 749.00, "SWIGGY_PAY", "JUSPAY", "2026-10-20T19:30:00", "SUCCESS", "swg_pay_8837", None, None),
            ("TXN-8843", user_id, "CUST-101", "ORD-8808", 980.00, "UPI_PAYTM", "JUSPAY", "2026-10-20T13:00:00", "SUCCESS", "swg_pay_8843", None, None),
            ("TXN-8844", user_id, "CUST-101", "ORD-8809", 1150.00, "CREDIT_CARD", "RAZORPAY", "2026-10-19T20:00:00", "SUCCESS", "zom_pay_8844", None, None),
            ("TXN-8845", user_id, "CUST-101", "ORD-8810", 420.00, "UPI_PHONEPE", "JUSPAY", "2026-10-18T21:00:00", "SUCCESS", "swg_pay_8845", None, None),
            ("TXN-8846", user_id, "CUST-101", "ORD-8811", 630.00, "SWIGGY_PAY", "JUSPAY", "2026-10-19T12:00:00", "SUCCESS", "swg_pay_8846", None, None),

            # Payments Cases
            ("TXN-8822", user_id, "CUST-102", "ORD-5502", 2499.00, "CREDIT_CARD", "RAZORPAY", "2026-10-19T21:20:15", "SUCCESS", "rzp_test_8822b", None, "RF-40192"),
            ("TXN-8847", user_id, "CUST-101", "ORD-7002", 1999.00, "UPI_RAZORPAY", "RAZORPAY", "2026-10-20T09:00:00", "SUCCESS", "rzp_pay_8847", None, None),
            ("TXN-8848", user_id, "CUST-101", "ORD-7003", 3450.00, "NETBANKING_SBI", "PAYU", "2026-10-20T14:00:00", "PENDING", "payu_bill_8848", "BANK_SETTLEMENT_PENDING", None),

            # Subscriptions Cases
            ("TXN-9101", user_id, "CUST-101", "ORD-9101", 1499.00, "CREDIT_CARD_AUTO", "STRIPE", "2026-10-19T02:00:00", "SUCCESS", "sub_pay_9101", "RENEWAL_AFTER_CANCEL", None),
            ("TXN-9102", user_id, "CUST-101", "ORD-9102", 799.00, "UPI_AUTO_DEBIT", "RAZORPAY", "2026-10-19T02:05:00", "SUCCESS", "sub_pay_9102", "DUPLICATE_SUB_CHARGE", None),
            ("TXN-9103", user_id, "CUST-101", "ORD-9103", 1188.00, "CARD_RECURRING", "STRIPE", "2026-10-18T03:00:00", "SUCCESS", "sub_pay_9103", "DISPUTED_RENEWAL", None),

            # Digital Services
            ("TXN-9201", user_id, "CUST-101", "ORD-9201", 3599.00, "UPI_GPAY", "RAZORPAY", "2026-10-20T10:00:00", "SUCCESS", "tel_pay_9201", "RECHARGE_PACK_FAILED", None),
            ("TXN-9202", user_id, "CUST-101", "ORD-9202", 800.00, "WALLET_PAYTM", "PAYTM", "2026-10-20T08:30:00", "SUCCESS", "ptm_metro_9202", "METRO_GATE_UNCREDITED", None),

            # Utility & Services
            ("TXN-9301", user_id, "CUST-101", "ORD-9301", 1299.00, "UPI_PHONEPE", "RAZORPAY", "2026-10-19T11:00:00", "SUCCESS", "uc_pay_9301", None, None),
            ("TXN-9302", user_id, "CUST-101", "ORD-9302", 1400.00, "CREDIT_CARD", "PAYU", "2026-10-20T16:00:00", "SUCCESS", "bms_pay_9302", None, None),

            # High-Risk / Exception Cases
            ("TXN-9901", user_id, "CUST-103", "ORD-5503", 48500.00, "NETBANKING_HDFC", "PAYU", "2026-10-19T21:25:30", "SUCCESS", "payu_test_9901c", "TOR_PROXY_FLAG", None),
            ("TXN-9401", user_id, "CUST-101", "ORD-9401", 145000.00, "CREDIT_CARD_AMEX", "RAZORPAY", "2026-10-20T18:00:00", "SUCCESS", "rzp_tv_9401", "CEILING_EXCEEDED", None)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, txns)

        ords = [
            # Travel Orders
            ("ORD-5501", user_id, "CUST-101", 2499.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-19T21:14:00", "UNFULFILLED", "NONE", "RedBus", "BLR -> Mumbai Intercity Bus Ticket #RB-10291"),
            ("ORD-9001", user_id, "CUST-101", 2499.00, "CANCELLED", "PAID", "2026-10-19T09:00:00", "UNFULFILLED", "CANCELLED_36H_PRIOR", "RedBus", "Bengaluru -> Mumbai Bus #RB-10291 (Eligible Cancellation)"),
            ("ORD-9002", user_id, "CUST-101", 1850.00, "CANCELLED", "PAID", "2026-10-20T17:00:00", "UNFULFILLED", "CANCELLED_2H_PRIOR", "RedBus", "Delhi -> Manali Luxury Bus #RB-10492 (Late Ineligible)"),
            ("ORD-9003", user_id, "CUST-101", 6800.00, "CANCELLED", "PAID", "2026-10-18T11:00:00", "UNFULFILLED", "CANCELLED_FREE_WINDOW", "MakeMyTrip", "Grand Hyatt Goa Resort #MMT-HOTEL-771 (Free Cancellation)"),
            ("ORD-9004", user_id, "CUST-101", 4200.00, "CANCELLED", "PAID", "2026-10-19T15:00:00", "UNFULFILLED", "NON_REFUNDABLE_RATE", "MakeMyTrip", "Taj Santacruz Mumbai #MMT-HOTEL-882 (Non-Refundable Fare)"),
            ("ORD-9005", user_id, "CUST-101", 5890.00, "CANCELLED", "PAID", "2026-10-17T08:00:00", "UNFULFILLED", "AIRLINE_CANCELLED", "IndiGo", "IndiGo Delhi -> Bengaluru Non-Stop Flight #6E-512"),
            ("ORD-9006", user_id, "CUST-101", 18400.00, "ACTIVE", "PAID", "2026-10-16T19:00:00", "FULFILLED", "SCHEDULE_DISRUPTION", "Air India", "Air India Mumbai -> Dubai International Flight #AI-983"),

            # E-Commerce Orders
            ("ORD-8801", user_id, "CUST-101", 26990.00, "DELIVERED", "PAID", "2026-10-17T14:00:00", "FULFILLED", "WRONG_ITEM_CLAIMED", "Amazon", "Sony WH-1000XM5 (Delivered Wrong Wired Mouse)"),
            ("ORD-8802", user_id, "CUST-101", 14499.00, "DELIVERED", "PAID", "2026-10-18T16:00:00", "FULFILLED", "DAMAGED_CLAIMED", "Amazon", "LG 27-inch 4K Monitor (Cracked Screen on Arrival)"),
            ("ORD-8803", user_id, "CUST-101", 3999.00, "DELIVERED", "PAID", "2026-10-16T12:00:00", "FULFILLED", "MISSING_ITEM", "Flipkart", "Noise ColorFit Smartwatch 2-Pack (1 Item Missing)"),
            ("ORD-8804", user_id, "CUST-101", 59900.00, "DELIVERED", "PAID", "2026-10-15T18:00:00", "FULFILLED", "REPLACEMENT_REQUESTED", "Amazon", "Apple iPad Air 11-inch M2 (Defective Touchscreen)"),
            ("ORD-8806", user_id, "CUST-101", 2899.00, "DELIVERED", "PAID", "2026-09-15T11:00:00", "FULFILLED", "RETURN_WINDOW_EXPIRED", "Flipkart", "Puma Nitro High-Performance Running Shoes (32d Expired)"),
            ("ORD-8807", user_id, "CUST-101", 34999.00, "CANCELLED", "PAID", "2026-10-18T20:00:00", "UNFULFILLED", "DUPLICATE_CHECKOUT_CHARGE", "Amazon", "Amazon Kindle Scribe Digital Notebook (Duplicate Charge)"),

            # Food Delivery Orders
            ("ORD-8805", user_id, "CUST-101", 749.00, "DELIVERED", "PAID", "2026-10-20T19:30:00", "FULFILLED", "FOOD_SPILLAGE", "Swiggy", "Meghana Special Biryani (Food Spilled in Transit)"),
            ("ORD-8808", user_id, "CUST-101", 980.00, "DELIVERED", "PAID", "2026-10-20T13:00:00", "FULFILLED", "WRONG_ITEM_FOOD", "Swiggy", "McDonald's Family Gourmet Meal (Wrong Burger Received)"),
            ("ORD-8809", user_id, "CUST-101", 1150.00, "DELIVERED", "PAID", "2026-10-19T20:00:00", "FULFILLED", "MISSING_SIDE_ITEM", "Zomato", "Domino's Pizza Party Pack (Garlic Bread Missing)"),
            ("ORD-8810", user_id, "CUST-101", 420.00, "DELIVERED", "PAID", "2026-10-18T21:00:00", "FULFILLED", "DELAYED_COLD_FOOD", "Swiggy", "Subway 6-inch Combo (Arrived Cold After 95 mins)"),
            ("ORD-8811", user_id, "CUST-101", 630.00, "CANCELLED", "PAID", "2026-10-19T12:00:00", "UNFULFILLED", "RESTAURANT_CANCELLED", "Swiggy", "Pizza Hut Pan Pizza (Cancelled by Outlet)"),

            # Payments Orders
            ("ORD-5502", user_id, "CUST-102", 2499.00, "FAILED_REFUNDED", "REFUNDED", "2026-10-19T21:20:00", "UNFULFILLED", "PROCESSED", "Generic Merchant", "Electronics Accessory Cart"),
            ("ORD-7002", user_id, "CUST-101", 1999.00, "DELIVERED", "PAID", "2026-10-20T09:00:00", "FULFILLED", "DUPLICATE_PAYMENT_REVERSED", "Generic Merchant", "Razorpay Payment Gateway Double-Debit"),
            ("ORD-7003", user_id, "CUST-101", 3450.00, "PENDING", "PENDING_SETTLEMENT", "2026-10-20T14:00:00", "UNFULFILLED", "PAYMENT_PENDING", "Generic Merchant", "State Electricity Board Utility Bill"),

            # Subscriptions Orders
            ("ORD-9101", user_id, "CUST-101", 1499.00, "ACTIVE", "PAID", "2026-10-19T02:00:00", "FULFILLED", "CANCELLED_BEFORE_RENEWAL", "Generic Merchant", "Prime Annual Membership (Erroneous Renewal)"),
            ("ORD-9102", user_id, "CUST-101", 799.00, "ACTIVE", "PAID", "2026-10-19T02:05:00", "FULFILLED", "DUPLICATE_CHARGE", "Generic Merchant", "Monthly Cloud Storage Subscription (Duplicate Charge)"),
            ("ORD-9103", user_id, "CUST-101", 1188.00, "ACTIVE", "PAID", "2026-10-18T03:00:00", "FULFILLED", "DISPUTED_RENEWAL", "Generic Merchant", "Spotify Premium Family Plan (Auto-Renewal Dispute)"),

            # Digital Services Orders
            ("ORD-9201", user_id, "CUST-101", 3599.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-20T10:00:00", "UNFULFILLED", "RECHARGE_FAILED", "Generic Merchant", "Airtel 5G Prepaid Annual Recharge (Failed Pack Credit)"),
            ("ORD-9202", user_id, "CUST-101", 800.00, "FAILED", "CAPTURED_NO_ORDER", "2026-10-20T08:30:00", "UNFULFILLED", "PASS_CREDIT_FAILED", "Generic Merchant", "Paytm Metro Smart Card Top-Up (Uncredited)"),

            # Utility & Services Orders
            ("ORD-9301", user_id, "CUST-101", 1299.00, "CANCELLED", "PAID", "2026-10-19T11:00:00", "UNFULFILLED", "TECHNICIAN_NO_SHOW", "Urban Company", "Urban Company AC Deep Cleaning (Service No-Show)"),
            ("ORD-9302", user_id, "CUST-101", 1400.00, "CONFIRMED", "PAID", "2026-10-20T16:00:00", "FULFILLED", "CONFIRMATION_MISSING", "BookMyShow", "BookMyShow IMAX Avatar 3 (Confirmation SMS Missing)"),

            # High-Risk Orders
            ("ORD-5503", user_id, "CUST-103", 48500.00, "SECURITY_HOLD", "FLAGGED_REVIEW", "2026-10-19T21:25:00", "HELD", "UNDER_REVIEW", "Amazon", "Apple MacBook Pro M3 (High Risk)"),
            ("ORD-9401", user_id, "CUST-101", 145000.00, "SECURITY_HOLD", "FLAGGED_REVIEW", "2026-10-20T18:00:00", "HELD", "CEILING_EXCEEDED", "Flipkart", "Samsung 85-inch Neo QLED 8K Smart TV (Disbursement Ceiling)")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ords)

        refs = [
            ("RF-40192", user_id, "TXN-8822", 2499.00, "PROCESSING", "2026-10-19T21:22:00", "2026-10-22T18:00:00", "ARN-9928172645-UPI", "Automated Batch")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO refunds (refund_id, user_id, transaction_id, amount, status, initiated_timestamp, expected_completion, bank_reference, initiated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, refs)

        cases = [
            ("CASE-101", user_id, "CUST-101", "Money deducted ₹2499 but order failed", "PAYMENT_FAILURE", "HIGH", "OPEN", None, "2026-10-19T21:15:00"),
            ("CASE-102", user_id, "CUST-102", "Second inquiry about refund status for ORD-5502", "REFUND_STATUS", "MEDIUM", "RESOLVED", "ARN-9928172645-UPI provided", "2026-10-19T21:23:00"),
            ("CASE-103", user_id, "CUST-103", "Order held on security verification ₹48,500", "SECURITY_VERIFICATION", "CRITICAL", "ESCALATED_TIER2", "Pending SecOps docket", "2026-10-19T21:26:00")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO support_cases (case_id, user_id, customer_id, issue, category, severity, status, resolution, created_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cases)

        audit_entries = [
            (user_id, "Planner", "PLAN_DECOMPOSE", "2026-10-19T21:14:05", "COMPOSE_DAG", "Formulated 7-stage plan for PG_504", "INITIALIZED"),
            (user_id, "Research", "POLICY_MATCH", "2026-10-19T21:14:06", "MATCH_POL_REF_01", "Retrieved Instant Auto-Refund Policy", "GATHERED"),
            (user_id, "Critic", "PRE_VALIDATE", "2026-10-19T21:14:07", "APPROVE", "5/5 safety checks passed. Low risk authorized.", "VALIDATED")
        ]
        cur.executemany("""
        INSERT INTO audit_logs (user_id, agent, action, timestamp, decision, result, state_transition)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, audit_entries)

    def _seed_evaluator_data(self, cur, user_id: str):
        """Seeds comprehensive benchmark and evaluator dataset (including 50+ systemic batch and all test cases)."""
        # Seeds the 30 curated cases first
        self._seed_rahul_data(cur, user_id)

        # Expand with 55 synthetic customers
        regions = ["Delhi, DL", "Bengaluru, KA", "Mumbai, MH", "Hyderabad, TS", "Chennai, TN", "Pune, MH", "Kolkata, WB", "Jaipur, RJ"]
        names = ["Aarav Gupta", "Sneha Rao", "Kabir Sen", "Meera Nair", "Arjun Das", "Diya Kapoor", "Varun Joshi", "Ishita Saxena"]
        extra_custs = []
        for i in range(1, 56):
            cid = f"CUST-2{i:02d}"
            cname = f"{names[i % len(names)]} {i}"
            cemail = f"user{i:02d}@megacorp.in"
            cphone = f"+91-980000{i:04d}"
            cregion = regions[i % len(regions)]
            trust = 85 + (i % 14)
            extra_custs.append((cid, user_id, cname, cemail, cphone, 12 + (i % 24), trust, cregion, "ACTIVE", 0))

        cur.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, extra_custs)

        # Systemic incident batch (50 transactions & orders with PG_TIMEOUT_504)
        extra_txns = []
        extra_ords = []
        for i in range(1, 101):
            tid = f"TXN-7{i:03d}"
            oid = f"ORD-7{i:03d}"
            cid = f"CUST-2{(i % 55) + 1:02d}"
            amt = 1999.00 if i <= 50 else (499.00 + (i * 25))
            err = "PG_TIMEOUT_504" if i <= 50 else None
            gate = "RAZORPAY" if i <= 60 else "PAYU"
            method = "UPI" if i % 2 == 0 else "CARD"
            extra_txns.append((tid, user_id, cid, oid, amt, method, gate, f"2026-10-19T21:{i%60:02d}:00", "SUCCESS", f"gtw_ref_{i:04d}", err, None))

            ostat = "FAILED" if i <= 50 else "DELIVERED"
            pstat = "CAPTURED_NO_ORDER" if i <= 50 else "PAID"
            prov = "Razorpay Gateway" if i <= 50 else "Generic Merchant"
            extra_ords.append((oid, user_id, cid, amt, ostat, pstat, f"2026-10-19T21:{i%60:02d}:00", "UNFULFILLED" if i <= 50 else "FULFILLED", "NONE", prov, f"Item SKU #{oid}"))

        cur.executemany("""
        INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, extra_txns)

        cur.executemany("""
        INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, extra_ords)

        # Seed Master Incident
        incidents = [
            ("INC-2026-SYS", user_id, "PG_TIMEOUT_504", 50, 50, "HIGH", "CLUSTER_RESOLVED", "Razorpay callback dropout during peak checkout rush", "Auto-remediation rule synthesized and promoted", "2026-10-19T21:32:00")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO incidents (incident_id, user_id, error_signature, affected_customers, affected_transactions, severity, status, root_pattern, remediation_rule, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, incidents)

    def _seed_dynamic_user_data(self, cur, user_id: str):
        """Seeds clean, isolated realistic dataset for dynamically registered users."""
        cur.execute("SELECT username, email FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        uname = row["username"] if row else "New Customer"
        uemail = row["email"] if row else f"{user_id}@resolvex.ai"
        cid = f"CUST-{user_id[-6:]}"

        custs = [
            (cid, user_id, uname, uemail, "+91-9800001122", 1, 95, "Bengaluru, KA", "ACTIVE", 0)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO customers (customer_id, user_id, name, email, phone, account_age_months, trust_score, region, status, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, custs)

        txns = [
            (f"TXN-{user_id[-6:]}-01", user_id, cid, f"ORD-{user_id[-6:]}-TRV", 4200.00, "CREDIT_CARD", "PAYU", "2026-10-20T10:00:00", "SUCCESS", f"gtw_{user_id[-6:]}_01", None, None),
            (f"TXN-{user_id[-6:]}-02", user_id, cid, f"ORD-{user_id[-6:]}-ECM", 1999.00, "UPI", "RAZORPAY", "2026-10-19T14:30:00", "SUCCESS", f"gtw_{user_id[-6:]}_02", None, None),
            (f"TXN-{user_id[-6:]}-03", user_id, cid, f"ORD-{user_id[-6:]}-FD", 680.00, "UPI", "JUSPAY", "2026-10-20T19:00:00", "SUCCESS", f"gtw_{user_id[-6:]}_03", None, None)
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO transactions (transaction_id, user_id, customer_id, order_id, amount, payment_method, gateway, timestamp, status, gateway_ref, error_code, refund_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, txns)

        ords = [
            (f"ORD-{user_id[-6:]}-TRV", user_id, cid, 4200.00, "DELIVERED", "PAID", "2026-10-20T10:00:00", "FULFILLED", "NONE", "MakeMyTrip", "Mumbai Weekend Hotel Booking"),
            (f"ORD-{user_id[-6:]}-ECM", user_id, cid, 1999.00, "DELIVERED", "PAID", "2026-10-19T14:30:00", "FULFILLED", "NONE", "Amazon", "Wireless Bluetooth Noise-Cancelling Earbuds"),
            (f"ORD-{user_id[-6:]}-FD", user_id, cid, 680.00, "DELIVERED", "PAID", "2026-10-20T19:00:00", "FULFILLED", "NONE", "Swiggy", "Express Dinner Gourmet Meal Combo")
        ]
        cur.executemany("""
        INSERT OR REPLACE INTO orders (order_id, user_id, customer_id, amount, order_status, payment_status, creation_timestamp, fulfilment_status, cancellation_status, provider, item_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ords)

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
        ident = (username_or_email or "").strip()
        if ident.lower() == "rahul":
            ident = "customer_demo"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, username, email, password_hash, role FROM users WHERE username = ? OR email = ?",
                (ident, ident)
            )
            row = cur.fetchone()
            if not row:
                return False, "Invalid credentials.", None

            user_id, username, email, pwd_hash, role = row["user_id"], row["username"], row["email"], row["password_hash"], row["role"]
            if not verify_password(password, pwd_hash):
                return False, "Invalid credentials.", None

            # Persistent chat session for registered users, fresh session for guests
            cur.execute("SELECT session_id FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
            last_sess = cur.fetchone()
            session_id = last_sess["session_id"] if last_sess else f"SESS-{user_id}"

            cur.execute("INSERT OR REPLACE INTO sessions (session_id, user_id, created_at) VALUES (?, ?, ?)", (session_id, user_id, datetime.now().isoformat()))
            conn.commit()

            display_name = "Jaydev Butani" if user_id == "USER-JAYDEV" else ("Rajvi Patel" if user_id == "USER-RAJVI" else ("Rahul Sharma" if user_id == "USER-CUST-DEMO" else username))

            return True, "Login successful.", {
                "user_id": user_id,
                "username": display_name,
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
