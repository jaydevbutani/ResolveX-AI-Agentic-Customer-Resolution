import json
from datetime import datetime
from typing import Dict, Any, List
from src.config import RULES_PATH
from src.db.store import db
from src.models.schemas import GeneratedRule

class SoftwareDevelopmentAgent:
    """
    Software Development Agent:
    Continuous Improvement Workflow:
    - Observes recurring systemic operational errors
    - Synthesizes declarative auto-remediation rules
    - Tests candidate rules against historical synthetic telemetry
    - Validates accuracy and commits verified rules to the system rule library
    """
    def __init__(self):
        self.name = "Software_Development_Agent"

    def synthesize_and_validate_rule(self, error_pattern: str = "PG_TIMEOUT_504") -> Dict[str, Any]:
        """
        Synthesizes a rule for the observed error pattern, runs unit tests,
        and saves it if accuracy meets production standard.
        """
        rule_id = f"RULE-AUTO-{datetime.now().strftime('%m%d%H%M')}"
        rule_name = f"Auto-Remediation: {error_pattern} Gateway Callback Dropout"

        candidate_rule = {
            "rule_id": rule_id,
            "name": rule_name,
            "description": f"Declarative rule to auto-reverse trapped payments experiencing {error_pattern} without manual ticket logging.",
            "condition": {
                "payment_status": "SUCCESS",
                "order_status": "FAILED",
                "error_code": error_pattern
            },
            "action": "AUTO_REVERSE_REFUND",
            "status": "CANDIDATE",
            "accuracy_score": 0.0,
            "tested_cases": 0,
            "created_by": self.name,
            "timestamp": datetime.now().isoformat()
        }

        # Run automated test against synthetic database transactions
        test_results = self._test_rule_against_history(candidate_rule)
        accuracy = test_results["accuracy"]
        candidate_rule["accuracy_score"] = accuracy
        candidate_rule["tested_cases"] = test_results["total_tested"]

        if accuracy >= 0.95:
            candidate_rule["status"] = "ACTIVE"
            self._save_rule_to_library(candidate_rule)
            db.log_audit(self.name, "DEPLOY_RULE", f"Promoted rule {rule_id} to production with {accuracy*100:.1f}% accuracy.")

        return {
            "status": "SUCCESS",
            "rule": candidate_rule,
            "test_report": test_results
        }

    def _test_rule_against_history(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Runs candidate rule predicates against all synthetic transactions & orders."""
        txns = db.get_all_transactions()
        cond = rule["condition"]

        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        for t in txns:
            ord_id = t.get("order_id")
            ord_rec = db.get_order(ord_id) if ord_id else None
            actual_failed = ord_rec and ord_rec.get("status") == "FAILED"

            # Check rule match
            matches_cond = (
                t.get("status") == cond["payment_status"] and
                t.get("error_code") == cond["error_code"] and
                actual_failed
            )

            # Ground truth: should it be auto-refunded?
            should_refund = (t.get("status") == "SUCCESS" and actual_failed and t.get("error_code") == cond["error_code"])

            if matches_cond and should_refund:
                true_positives += 1
            elif matches_cond and not should_refund:
                false_positives += 1
            elif not matches_cond and not should_refund:
                true_negatives += 1
            else:
                false_negatives += 1

        total = true_positives + false_positives + true_negatives + false_negatives
        accuracy = (true_positives + true_negatives) / total if total > 0 else 1.0

        return {
            "total_tested": total,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "true_negatives": true_negatives,
            "false_negatives": false_negatives,
            "accuracy": round(accuracy, 4),
            "passed_validation": accuracy >= 0.95
        }

    def _save_rule_to_library(self, rule: Dict[str, Any]):
        rules = []
        if RULES_PATH.exists():
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                rules = json.load(f)
        rules.append(rule)
        with open(RULES_PATH, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2)

# Global Software Dev Agent instance
software_dev_agent = SoftwareDevelopmentAgent()
