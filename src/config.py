import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DB_PATH = DATA_DIR / "synthetic_db.json"
SYNTHETIC_DB_TEMPLATE_PATH = DATA_DIR / "synthetic_db_template.json"
POLICIES_PATH = DATA_DIR / "policies.json"
RULES_PATH = DATA_DIR / "rules.json"

# LLM Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "25"))
DEFAULT_REASONING_MODE = os.getenv("RESOLVEX_MODE", "FALLBACK") # "OLLAMA", "FALLBACK", "HYBRID"

# Autonomy Thresholds
MAX_AUTONOMOUS_REFUND_INR = 25000.0
MIN_CUSTOMER_TRUST_SCORE = 50
SYSTEMIC_INCIDENT_THRESHOLD = 5

# System Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
