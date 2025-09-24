"""
Phase-1 Securitization QA Micro-Suite
5-minute validation checks before canary widening
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import numpy as np


class SecuritizationQASuite:
    """QA validation suite for Phase-1 securitization structures"""

    def __init__(self):
        self.tolerance_dscr = 0.001
        self.tolerance_wal = 0.1  # years
        self.tolerance_value = 1.0  # currency units
        self.required_near_misses = 3
        self.results = {}
        self.blocking_errors = []

    def run_all_checks(self, structure_data: Dict) -> Dict:
        """Run complete QA suite on winning structure"""
        print("[QA] Starting securitization QA micro-suite...")
        start_time = time.time()

        # Initialize results
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "structure_id": structure_data.get("structure_id"),
            "checks": {},
            "blocking_errors": [],
            "pass": True
        }

        # Run individual checks
        checks = [
            ("reverse_dscr", self.check_reverse_dscr),
            ("wal_senior", self.check_wal),
            ("tenor_guardrail", self.check_tenor_guardrail),
            ("repo_rule_key", self.check_repo_rule_key),
            ("indexation_split", self.check_indexation_split),
            ("sidecar_reconciliation", self.check_sidecar_reconciliation),
            ("near_miss_hints", self.check_near_miss_hints)
        ]

        for check_name, check_func in checks:
            try:
                result = check_func(structure_data)
                self.results["checks"][check_name] = result

                if not result.get("pass", False):
                    self.blocking_errors.append({
                        "check": check_name,
                        "error": result.get("error", "Check failed"),
                        "details": result.get("details")
                    })
                    self.results["pass"] = False

            except Exception as e:
                self.results["checks"][check_name] = {
                    "pass": False,
                    "error": str(e)
                }
                self.blocking_errors.append({
                    "check": check_name,
                    "error": f"Exception: {str(e)}"
                })
                self.results["pass"] = False

        # Compile results
        self.results["blocking_errors"] = self.blocking_errors
        self.results["execution_time"] = time.time() - start_time

        return self.results

    def check_reverse_dscr(self, data: Dict) -> Dict:
        """Validate DSCR calculation from schedule"""
        schedule = data.get("payment_schedule", {})
        senior_data = schedule.get("senior", {})

        # Extract components
        noi = data.get("net_operating_income", 0)
        senior_fees = data.get("senior_fees", 0)

        # Calculate from schedule
        total_interest = sum(senior_data.get("interest_payments", []))
        total_principal = sum(senior_data.get("principal_payments", []))
        required_reserves = data.get("required_reserves", 0)

        # Compute DSCR
        numerator = noi - senior_fees
        denominator = total_interest + total_principal + required_reserves

        if denominator > 0:
            computed_dscr = numerator / denominator
        else:
            return {
                "pass": False,
                "error": "Invalid denominator in DSCR calculation",
                "details": {
                    "numerator": numerator,
                    "denominator": denominator
                }
            }

        # Compare with reported
        reported_dscr = data.get("dscr", 0)
        difference = abs(computed_dscr - reported_dscr)

        return {
            "pass": difference <= self.tolerance_dscr,
            "computed": computed_dscr,
            "reported": reported_dscr,
            "difference": difference,
            "tolerance": self.tolerance_dscr,
            "components": {
                "noi": noi,
                "senior_fees": senior_fees,
                "interest": total_interest,
                "principal": total_principal,
                "reserves": required_reserves
            }
        }

    def check_wal(self, data: Dict) -> Dict:
        """Validate Weighted Average Life for senior tranche"""
        schedule = data.get("payment_schedule", {})
        senior_data = schedule.get("senior", {})

        principal_payments = senior_data.get("principal_payments", [])
        payment_dates = senior_data.get("payment_dates", [])

        if not principal_payments or not payment_dates:
            return {
                "pass": False,
                "error": "Missing payment schedule data"
            }

        # Calculate WAL
        total_principal = sum(principal_payments)
        if total_principal == 0:
            return {
                "pass": False,
                "error": "Zero total principal"
            }

        wal = 0
        for i, (principal, date) in enumerate(zip(principal_payments, payment_dates)):
            years_from_start = (i + 1) / 12  # Assuming monthly payments
            weight = principal / total_principal
            wal += weight * years_from_start

        # Compare with reported
        reported_wal = data.get("senior_wal", 0)
        difference = abs(wal - reported_wal)

        return {
            "pass": difference <= self.tolerance_wal,
            "computed": wal,
            "reported": reported_wal,
            "difference": difference,
            "tolerance": self.tolerance_wal,
            "total_principal": total_principal
        }

    def check_tenor_guardrail(self, data: Dict) -> Dict:
        """Verify senior tenor vs lease years"""
        senior_tenor = data.get("senior_tenor", 0)
        lease_years = data.get("lease_years", 0)
        buffer_years = data.get("tenor_buffer", 2)

        max_allowed = lease_years - buffer_years

        return {
            "pass": senior_tenor <= max_allowed,
            "senior_tenor": senior_tenor,
            "lease_years": lease_years,
            "buffer": buffer_years,
            "max_allowed": max_allowed,
            "breach": senior_tenor > max_allowed
        }

    def check_repo_rule_key(self, data: Dict) -> Dict:
        """Validate repo eligibility rule key"""
        rule_key = data.get("repo_rule_key", {})

        required_components = [
            "jurisdiction",
            "issuer_form",
            "currency",
            "doc_standard",
            "settlement"
        ]

        missing = []
        for component in required_components:
            if component not in rule_key:
                missing.append(component)

        repo_status = data.get("repo_eligibility", {})
        repo_pass = repo_status.get("eligible", False)
        repo_reason = repo_status.get("reason", "")

        if not repo_pass and not repo_reason:
            return {
                "pass": False,
                "error": "Repo FAIL without reason",
                "rule_key": rule_key,
                "missing_components": missing
            }

        return {
            "pass": len(missing) == 0 and (repo_pass or bool(repo_reason)),
            "rule_key": rule_key,
            "repo_eligible": repo_pass,
            "repo_reason": repo_reason,
            "missing_components": missing
        }

    def check_indexation_split(self, data: Dict) -> Dict:
        """Verify indexation handling for flatten_core mode"""
        flatten_core = data.get("flatten_core", False)

        if not flatten_core:
            return {
                "pass": True,
                "flatten_core": False,
                "message": "Flatten core not enabled"
            }

        core_cashflows = data.get("core_cashflows", {})
        sidecar_data = data.get("sidecar", {})

        # Check core is flat/capped
        core_indexed = core_cashflows.get("has_indexation", False)
        core_capped = core_cashflows.get("indexation_capped", False)

        # Check excess in sidecar
        sidecar_has_excess = sidecar_data.get("excess_indexation", False)

        valid = (not core_indexed or core_capped) and sidecar_has_excess

        return {
            "pass": valid,
            "flatten_core": True,
            "core_indexed": core_indexed,
            "core_capped": core_capped,
            "sidecar_has_excess": sidecar_has_excess,
            "split_confirmed": valid
        }

    def check_sidecar_reconciliation(self, data: Dict) -> Dict:
        """Reconcile sidecar day-one values"""
        sidecar = data.get("sidecar", {})

        sidecar_gross = sidecar.get("gross_value", 0)
        haircut_pct = sidecar.get("haircut_pct", 0)
        sidecar_net_reported = sidecar.get("net_value", 0)

        # Calculate expected net
        sidecar_net_computed = sidecar_gross * (1 - haircut_pct / 100)

        # Get total day-one values
        core_day_one = data.get("core_day_one_value", 0)
        total_day_one_reported = data.get("total_day_one_value", 0)
        total_day_one_computed = core_day_one + sidecar_net_computed

        # Check tolerances
        net_diff = abs(sidecar_net_computed - sidecar_net_reported)
        total_diff = abs(total_day_one_computed - total_day_one_reported)

        return {
            "pass": net_diff <= self.tolerance_value and total_diff <= self.tolerance_value,
            "sidecar_gross": sidecar_gross,
            "haircut_pct": haircut_pct,
            "sidecar_net_computed": sidecar_net_computed,
            "sidecar_net_reported": sidecar_net_reported,
            "net_difference": net_diff,
            "core_day_one": core_day_one,
            "total_computed": total_day_one_computed,
            "total_reported": total_day_one_reported,
            "total_difference": total_diff,
            "tolerance": self.tolerance_value
        }

    def check_near_miss_hints(self, data: Dict) -> Dict:
        """Verify near-miss structures have lever hints"""
        near_misses = data.get("near_miss_structures", [])

        valid_hints = []
        for miss in near_misses:
            hints = miss.get("lever_hints", [])
            if hints and any("DSCR" in h or "tenor" in h for h in hints):
                valid_hints.append({
                    "structure_id": miss.get("id"),
                    "hints": hints
                })

        has_enough = len(valid_hints) >= self.required_near_misses

        return {
            "pass": has_enough,
            "required": self.required_near_misses,
            "found": len(valid_hints),
            "valid_hints": valid_hints[:5],  # Show first 5
            "total_near_misses": len(near_misses)
        }


class GoNoGoGate:
    """Final go/no-go decision gate for canary deployment"""

    def __init__(self):
        self.criteria = {
            "error_rate_pct": 1.0,
            "p95_step_time_s": 2.0,
            "memory_drift": False,
            "qa_checks_pass": True,
            "repo_rule_pass": True,
            "rollback_ttr_s": 2.0,
            "logging_complete": True
        }
        self.decision = None
        self.reasons = []

    def evaluate(self, metrics: Dict, qa_results: Dict) -> Dict:
        """Evaluate all criteria for go/no-go decision"""
        print("[GATE] Evaluating go/no-go criteria...")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "criteria_met": {},
            "decision": "NO-GO",
            "reasons": [],
            "action": None
        }

        # Check each criterion
        checks = [
            ("error_rate", self._check_error_rate, metrics),
            ("p95_latency", self._check_p95_latency, metrics),
            ("memory_stability", self._check_memory, metrics),
            ("qa_suite", self._check_qa_suite, qa_results),
            ("repo_eligibility", self._check_repo, qa_results),
            ("rollback_ready", self._check_rollback, metrics),
            ("logging", self._check_logging, metrics)
        ]

        all_pass = True
        for check_name, check_func, check_data in checks:
            passed, reason = check_func(check_data)
            results["criteria_met"][check_name] = passed

            if not passed:
                all_pass = False
                results["reasons"].append(f"{check_name}: {reason}")

        # Make decision
        if all_pass:
            results["decision"] = "GO"
            results["action"] = "Proceed with canary widening from 1% to 25%"
        else:
            results["decision"] = "NO-GO"
            results["action"] = "Execute rollback, keep at 0%, post incident note"

        self.decision = results["decision"]
        self.reasons = results["reasons"]

        return results

    def _check_error_rate(self, metrics: Dict) -> Tuple[bool, str]:
        """Check error rate threshold"""
        error_rate = metrics.get("error_rate_pct", 100)
        passed = error_rate < self.criteria["error_rate_pct"]
        reason = f"Error rate {error_rate:.2f}% vs threshold {self.criteria['error_rate_pct']}%"
        return passed, reason

    def _check_p95_latency(self, metrics: Dict) -> Tuple[bool, str]:
        """Check P95 latency threshold"""
        p95 = metrics.get("p95_step_time_s", 999)
        passed = p95 < self.criteria["p95_step_time_s"]
        reason = f"P95 latency {p95:.2f}s vs threshold {self.criteria['p95_step_time_s']}s"
        return passed, reason

    def _check_memory(self, metrics: Dict) -> Tuple[bool, str]:
        """Check memory stability"""
        drift = metrics.get("memory_drift", True)
        passed = not drift
        reason = f"Memory drift detected" if drift else "Memory stable"
        return passed, reason

    def _check_qa_suite(self, qa_results: Dict) -> Tuple[bool, str]:
        """Check QA suite results"""
        passed = qa_results.get("pass", False)
        errors = qa_results.get("blocking_errors", [])
        reason = f"{len(errors)} blocking errors" if errors else "All QA checks passed"
        return passed, reason

    def _check_repo(self, qa_results: Dict) -> Tuple[bool, str]:
        """Check repo eligibility"""
        repo_check = qa_results.get("checks", {}).get("repo_rule_key", {})
        passed = repo_check.get("repo_eligible", False)
        reason = repo_check.get("repo_reason", "No repo status")
        return passed, reason

    def _check_rollback(self, metrics: Dict) -> Tuple[bool, str]:
        """Check rollback readiness"""
        ttr = metrics.get("rollback_ttr_s", 999)
        passed = ttr < self.criteria["rollback_ttr_s"]
        reason = f"Rollback TTR {ttr:.2f}s vs threshold {self.criteria['rollback_ttr_s']}s"
        return passed, reason

    def _check_logging(self, metrics: Dict) -> Tuple[bool, str]:
        """Check logging completeness"""
        required_fields = ["seed", "chunk_id", "range_signature_hash", "ruleset_hash", "commit_sha"]
        present = metrics.get("log_fields_present", [])
        missing = [f for f in required_fields if f not in present]
        passed = len(missing) == 0
        reason = f"Missing log fields: {missing}" if missing else "All log fields present"
        return passed, reason


def generate_signature_hash(data: Dict) -> str:
    """Generate deterministic hash for range signature"""
    key_fields = [
        "structure_id",
        "senior_size",
        "dscr",
        "tenor",
        "jurisdiction"
    ]

    signature_input = "|".join(str(data.get(k, "")) for k in sorted(key_fields))
    return hashlib.sha256(signature_input.encode()).hexdigest()[:16]


def generate_ruleset_hash(ruleset: Dict) -> str:
    """Generate hash for ruleset version"""
    ruleset_str = json.dumps(ruleset, sort_keys=True)
    return hashlib.sha256(ruleset_str.encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Example test
    print("[QA] Securitization QA Suite Module Loaded")
    print("[QA] Ready for integration with Phase-1 system")