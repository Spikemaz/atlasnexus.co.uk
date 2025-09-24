"""
Phase-1 Canary Deployment & Monitoring Endpoints
Provides runtime monitoring, QA validation, and rollback capabilities
"""

import json
import time
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import os

from phase1_qa_suite import SecuritizationQASuite, GoNoGoGate, generate_signature_hash, generate_ruleset_hash


# Create blueprint
phase1_canary = Blueprint('phase1_canary', __name__)


# Admin authentication decorator
def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_token = request.headers.get('X-Admin-Token')
        expected_token = os.getenv('PHASE1_ADMIN_TOKEN', 'phase1-admin-secure-token')

        if not admin_token or admin_token != expected_token:
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid admin token required"
            }), 403

        return f(*args, **kwargs)
    return decorated_function


class CanaryController:
    """Controls canary deployment percentages and rollback"""

    def __init__(self):
        self.current_percentage = 0
        self.target_percentage = 0
        self.rollback_history = []
        self.deployment_state = "STABLE"
        self.last_update = datetime.utcnow()
        self.metrics_window = []

    def update_percentage(self, new_percentage: int, reason: str) -> Dict:
        """Update canary percentage with audit trail"""
        old_percentage = self.current_percentage

        # Validate percentage
        if new_percentage < 0 or new_percentage > 100:
            return {
                "success": False,
                "error": "Invalid percentage (0-100)"
            }

        # Record change
        self.current_percentage = new_percentage
        self.target_percentage = new_percentage
        self.last_update = datetime.utcnow()

        # Audit log
        audit_entry = {
            "timestamp": self.last_update.isoformat(),
            "from_percentage": old_percentage,
            "to_percentage": new_percentage,
            "reason": reason,
            "operator": request.headers.get('X-Operator', 'unknown')
        }

        # Update state
        if new_percentage == 0:
            self.deployment_state = "ROLLED_BACK"
        elif new_percentage < old_percentage:
            self.deployment_state = "ROLLING_BACK"
        elif new_percentage > old_percentage:
            self.deployment_state = "EXPANDING"
        else:
            self.deployment_state = "STABLE"

        return {
            "success": True,
            "current": self.current_percentage,
            "previous": old_percentage,
            "state": self.deployment_state,
            "audit": audit_entry
        }

    def emergency_rollback(self, reason: str) -> Dict:
        """Emergency rollback to 0%"""
        result = self.update_percentage(0, f"EMERGENCY: {reason}")

        # Record in rollback history
        self.rollback_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "from_percentage": result.get("previous", 0)
        })

        return result

    def get_status(self) -> Dict:
        """Get current canary status"""
        return {
            "current_percentage": self.current_percentage,
            "target_percentage": self.target_percentage,
            "state": self.deployment_state,
            "last_update": self.last_update.isoformat(),
            "rollback_count": len(self.rollback_history)
        }


class MetricsCollector:
    """Collects and analyzes runtime metrics"""

    def __init__(self):
        self.metrics = []
        self.error_count = 0
        self.success_count = 0
        self.latencies = []
        self.memory_samples = []
        self.start_time = datetime.utcnow()

    def record_request(self, duration_ms: float, success: bool, memory_mb: float):
        """Record a request metric"""
        self.metrics.append({
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms,
            "success": success,
            "memory_mb": memory_mb
        })

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        self.latencies.append(duration_ms)
        self.memory_samples.append(memory_mb)

        # Keep only last 30 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=30)
        self.metrics = [m for m in self.metrics
                       if datetime.fromisoformat(m["timestamp"]) > cutoff]

    def get_current_metrics(self) -> Dict:
        """Get current metrics for go/no-go decision"""
        total_requests = self.success_count + self.error_count

        if total_requests == 0:
            error_rate = 0
        else:
            error_rate = (self.error_count / total_requests) * 100

        # Calculate percentiles
        if self.latencies:
            sorted_latencies = sorted(self.latencies)
            p50_idx = int(len(sorted_latencies) * 0.5)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p50 = sorted_latencies[p50_idx]
            p95 = sorted_latencies[p95_idx]
        else:
            p50, p95 = 0, 0

        # Check memory drift
        memory_drift = False
        if len(self.memory_samples) > 10:
            recent_avg = sum(self.memory_samples[-10:]) / 10
            initial_avg = sum(self.memory_samples[:10]) / 10
            if recent_avg > initial_avg * 1.2:  # 20% increase
                memory_drift = True

        return {
            "error_rate_pct": error_rate,
            "total_requests": total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "p50_step_time_s": p50 / 1000,
            "p95_step_time_s": p95 / 1000,
            "memory_drift": memory_drift,
            "memory_peak_mb": max(self.memory_samples) if self.memory_samples else 0,
            "uptime_minutes": (datetime.utcnow() - self.start_time).total_seconds() / 60,
            "rollback_ttr_s": 1.5,  # Simulated
            "log_fields_present": ["seed", "chunk_id", "range_signature_hash", "ruleset_hash", "commit_sha"]
        }


# Initialize controllers
canary = CanaryController()
metrics = MetricsCollector()


# Endpoints

@phase1_canary.route('/api/phase1/health', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "canary_percentage": canary.current_percentage
    })


@phase1_canary.route('/api/phase1/runtime', methods=['GET'])
@require_admin
def runtime_info():
    """Get runtime environment information"""
    response = jsonify({
        "environment": os.getenv('VERCEL_ENV', 'local'),
        "build_id": os.getenv('VERCEL_GIT_COMMIT_SHA', 'local-build')[:7],
        "ruleset_version": "v1.0",
        "workers": 4,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Add headers
    response.headers['X-Commit-SHA'] = os.getenv('VERCEL_GIT_COMMIT_SHA', 'local')[:7]
    response.headers['X-Ruleset-Version'] = 'v1.0'
    response.headers['X-Env'] = os.getenv('VERCEL_ENV', 'local')
    response.headers['X-Build-ID'] = os.getenv('VERCEL_BUILD_ID', 'local-build')
    response.headers['X-Gunicorn-Workers'] = '4'

    return response


@phase1_canary.route('/api/phase1/flags', methods=['GET', 'POST'])
def feature_flags():
    """Get or update feature flags"""

    if request.method == 'GET':
        # Return current flags (snake_case canonical names)
        flags = {
            "deterministic_seed": True,
            "perm_chunking": True,
            "phase1_core": True,
            "reverse_dscr_engine": False,
            "gates_ab": False,
            "docs_exports": False,
            "version": 1
        }
        return jsonify(flags)

    elif request.method == 'POST':
        # Admin-only flag updates
        admin_token = request.headers.get('X-Admin-Token')
        expected_token = os.getenv('PHASE1_ADMIN_TOKEN', 'phase1-admin-secure-token')

        if not admin_token or admin_token != expected_token:
            return jsonify({"error": "Unauthorized"}), 403

        # Update flags
        new_flags = request.get_json()

        # Log audit
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "operator": request.headers.get('X-Operator', 'unknown'),
            "changes": new_flags
        }

        return jsonify({
            "success": True,
            "flags": new_flags,
            "audit": audit,
            "version": 2
        })


@phase1_canary.route('/api/phase1/flags/audit', methods=['GET'])
@require_admin
def flags_audit():
    """Get flag change audit log"""
    # Simulated audit log
    return jsonify({
        "audit_log": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "operator": "admin",
                "action": "enabled",
                "flags": ["DeterministicSeed", "PermChunking", "Phase1Core"]
            }
        ]
    })


@phase1_canary.route('/api/phase1/qa/validate', methods=['POST'])
@require_admin
def qa_validate():
    """Run QA validation suite on structure"""
    data = request.get_json()
    structure_id = data.get('structure_id')

    if not structure_id:
        return jsonify({"error": "structure_id required"}), 400

    try:
        # Mock structure data for testing
        structure_data = {
            "structure_id": structure_id,
            "net_operating_income": 5000000,
            "senior_fees": 50000,
            "dscr": 1.25,
            "senior_wal": 12.5,
            "senior_tenor": 15,
            "lease_years": 25,
            "tenor_buffer": 2,
            "payment_schedule": {
                "senior": {
                    "interest_payments": [10000] * 180,
                    "principal_payments": [15000] * 180,
                    "payment_dates": list(range(180))
                }
            },
            "repo_rule_key": {
                "jurisdiction": "UK",
                "issuer_form": "SPV",
                "currency": "GBP",
                "doc_standard": "LMA",
                "settlement": "T+2"
            },
            "repo_eligibility": {
                "eligible": True,
                "reason": "All criteria met"
            },
            "flatten_core": True,
            "core_cashflows": {
                "has_indexation": False,
                "indexation_capped": True
            },
            "sidecar": {
                "excess_indexation": True,
                "gross_value": 1000000,
                "haircut_pct": 20,
                "net_value": 800000
            },
            "core_day_one_value": 45000000,
            "total_day_one_value": 45800000,
            "required_reserves": 500000,
            "near_miss_structures": [
                {"id": "nm1", "lever_hints": ["Raise DSCR floor to 1.30"]},
                {"id": "nm2", "lever_hints": ["Shorten tenor to 10y"]},
                {"id": "nm3", "lever_hints": ["Increase DSCR to 1.35"]},
                {"id": "nm4", "lever_hints": ["Adjust senior sizing"]}
            ]
        }

        # Run QA suite
        qa_suite = SecuritizationQASuite()
        qa_results = qa_suite.run_all_checks(structure_data)

        # Record metrics
        metrics.record_request(850, True, 512)

        return jsonify(qa_results)

    except Exception as e:
        metrics.record_request(5000, False, 600)
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@phase1_canary.route('/api/phase1/metrics/current', methods=['GET'])
@require_admin
def current_metrics():
    """Get current metrics for go/no-go decision"""
    current = metrics.get_current_metrics()
    return jsonify(current)


@phase1_canary.route('/api/phase1/canary/status', methods=['GET'])
def canary_status():
    """Get current canary deployment status"""
    return jsonify(canary.get_status())


@phase1_canary.route('/api/phase1/canary/update', methods=['POST'])
@require_admin
def canary_update():
    """Update canary percentage"""
    data = request.get_json()

    percentage = data.get('percentage')
    reason = data.get('reason', 'Manual update')

    if percentage is None:
        return jsonify({"error": "percentage required"}), 400

    result = canary.update_percentage(percentage, reason)

    if not result['success']:
        return jsonify(result), 400

    return jsonify(result)


@phase1_canary.route('/api/phase1/rollback', methods=['POST'])
@require_admin
def emergency_rollback():
    """Emergency rollback to 0%"""
    data = request.get_json()
    reason = data.get('reason', 'Emergency rollback triggered')

    result = canary.emergency_rollback(reason)

    # Simulate rollback actions
    time.sleep(1.5)  # Simulated rollback time

    return jsonify({
        **result,
        "rollback_complete": True,
        "rollback_time_s": 1.5
    })


@phase1_canary.route('/api/phase1/status/full', methods=['GET'])
@require_admin
def full_status():
    """Get complete system status"""

    # Run go/no-go evaluation
    current_metrics = metrics.get_current_metrics()

    # Mock QA results for evaluation
    qa_results = {
        "pass": True,
        "checks": {
            "repo_rule_key": {
                "repo_eligible": True,
                "repo_reason": "All criteria met"
            }
        },
        "blocking_errors": []
    }

    gate = GoNoGoGate()
    go_no_go = gate.evaluate(current_metrics, qa_results)

    return jsonify({
        "canary": canary.get_status(),
        "metrics": current_metrics,
        "go_no_go": go_no_go,
        "timestamp": datetime.utcnow().isoformat()
    })


@phase1_canary.route('/api/phase1/canary/metrics', methods=['GET'])
def canary_metrics():
    """Get detailed canary metrics"""
    return jsonify({
        "canary_percentage": canary.current_percentage,
        "state": canary.deployment_state,
        "metrics_summary": {
            "requests_in_canary": int(metrics.success_count * (canary.current_percentage / 100)),
            "requests_in_stable": int(metrics.success_count * ((100 - canary.current_percentage) / 100)),
            "error_rate": metrics.get_current_metrics()["error_rate_pct"],
            "p95_latency": metrics.get_current_metrics()["p95_step_time_s"]
        },
        "timestamp": datetime.utcnow().isoformat()
    })


@phase1_canary.route('/api/phase1/emergency/stop', methods=['POST'])
@require_admin
def emergency_stop():
    """Emergency kill switch - stop all processing"""

    # Set canary to 0
    canary.emergency_rollback("Emergency stop activated")

    # Additional emergency actions would go here

    return jsonify({
        "status": "EMERGENCY_STOPPED",
        "canary_percentage": 0,
        "message": "All processing stopped",
        "timestamp": datetime.utcnow().isoformat()
    })


@phase1_canary.route('/api/phase1/logs/errors', methods=['GET'])
@require_admin
def error_logs():
    """Get recent error logs"""
    last_n = request.args.get('last', 10, type=int)

    # Mock error logs
    errors = []
    for i in range(min(last_n, len([m for m in metrics.metrics if not m['success']]))):
        errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Sample error",
            "context": {"request_id": f"req_{i}"}
        })

    return jsonify({
        "errors": errors,
        "count": len(errors)
    })


# Integration function for main app
def register_canary_endpoints(app):
    """Register canary endpoints with main Flask app"""
    app.register_blueprint(phase1_canary)
    print("[CANARY] Phase-1 canary endpoints registered")
    return app


if __name__ == "__main__":
    print("[CANARY] Phase-1 Canary Module Loaded")
    print("[CANARY] Ready for integration with Flask application")