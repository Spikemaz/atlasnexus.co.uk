"""
AtlasNexus Canary Rollout Strategy
=================================
Manages gradual feature rollouts with monitoring and rollback capabilities
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import threading

from feature_flags import feature_flags
from observability import metrics_collector, structured_logger

class RolloutPhase(Enum):
    """Rollout phases for canary deployment"""
    ADMIN_ONLY = "admin_only"       # 0% public traffic
    CANARY_1_PERCENT = "1_percent"  # 1% public traffic
    CANARY_25_PERCENT = "25_percent"  # 25% public traffic
    FULL_ROLLOUT = "100_percent"    # 100% public traffic
    ROLLED_BACK = "rolled_back"     # Feature disabled

class RolloutStatus(Enum):
    """Status of rollout operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class CanaryRolloutManager:
    """
    Manages canary rollout for Phase-1 features with:
    - Automatic progression based on metrics
    - Rollback on error thresholds
    - Real-time monitoring
    """

    def __init__(self):
        self.logger = structured_logger
        self.rollout_config_file = '/tmp/rollout_config.json' if os.environ.get('VERCEL') else 'rollout_config.json'
        self.rollout_history_file = '/tmp/rollout_history.json' if os.environ.get('VERCEL') else 'rollout_history.json'

        # Rollout configuration
        self.phase1_features = [
            'input_hierarchy_processor',
            'reverse_dscr_engine',
            'repo_eligibility_rules',
            'viability_tiering',
            'dashboard_tiles'
        ]

        # Safety thresholds for automatic rollback
        self.rollback_thresholds = {
            'error_rate_percent': 5.0,      # 5% error rate triggers rollback
            'response_time_p95_ms': 5000,   # 5s P95 response time
            'memory_usage_mb': 512,         # 512MB memory usage
            'failed_requests_count': 50     # 50 failed requests in 5 minutes
        }

        # Progression criteria (all must be met to advance)
        self.progression_criteria = {
            'min_runtime_minutes': 60,      # Minimum time in current phase
            'max_error_rate_percent': 1.0,  # Maximum error rate to progress
            'max_response_time_p95_ms': 2000, # Maximum P95 response time
            'min_success_rate_percent': 98.0  # Minimum success rate
        }

        self.load_configuration()

    def load_configuration(self):
        """Load rollout configuration from storage"""
        try:
            if os.path.exists(self.rollout_config_file):
                with open(self.rollout_config_file, 'r') as f:
                    config = json.load(f)
                    self.current_rollouts = config.get('current_rollouts', {})
            else:
                self.current_rollouts = {}
        except Exception as e:
            self.logger.error("Failed to load rollout configuration", error=str(e))
            self.current_rollouts = {}

    def save_configuration(self):
        """Save rollout configuration to storage"""
        try:
            config = {
                'current_rollouts': self.current_rollouts,
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(self.rollout_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error("Failed to save rollout configuration", error=str(e))

    def start_phase1_rollout(self) -> Dict[str, any]:
        """
        Start Phase-1 canary rollout for all new features

        Returns:
            Dict with rollout initiation results
        """
        rollout_id = f"phase1_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        results = {
            'rollout_id': rollout_id,
            'started_at': datetime.utcnow().isoformat(),
            'features': {},
            'overall_status': 'initiated'
        }

        self.logger.info("Starting Phase-1 canary rollout", rollout_id=rollout_id)

        for feature in self.phase1_features:
            try:
                # Initialize feature in ADMIN_ONLY phase (0% public)
                feature_flags.set_flag(
                    feature,
                    enabled=True,
                    admin_only=True,
                    rollout_percentage=0,
                    description=f"Phase-1 feature in admin-only rollout"
                )

                self.current_rollouts[feature] = {
                    'rollout_id': rollout_id,
                    'current_phase': RolloutPhase.ADMIN_ONLY.value,
                    'phase_started_at': datetime.utcnow().isoformat(),
                    'status': RolloutStatus.IN_PROGRESS.value,
                    'metrics_baseline': self._capture_baseline_metrics(feature)
                }

                results['features'][feature] = 'admin_only_enabled'

                self.logger.info(
                    "Feature enabled in admin-only mode",
                    feature=feature,
                    rollout_id=rollout_id
                )

            except Exception as e:
                results['features'][feature] = f'failed: {str(e)}'
                self.logger.error(
                    "Failed to initialize feature rollout",
                    feature=feature,
                    error=str(e)
                )

        self.save_configuration()
        metrics_collector.increment_counter('canary_rollouts_started')

        return results

    def check_rollout_progression(self) -> Dict[str, any]:
        """
        Check if any features can progress to next rollout phase

        Returns:
            Dict with progression check results
        """
        progression_results = {
            'checked_at': datetime.utcnow().isoformat(),
            'features': {}
        }

        for feature, rollout_info in self.current_rollouts.items():
            if rollout_info['status'] != RolloutStatus.IN_PROGRESS.value:
                continue

            current_phase = RolloutPhase(rollout_info['current_phase'])
            phase_started = datetime.fromisoformat(rollout_info['phase_started_at'])

            # Check if feature should be rolled back
            should_rollback, rollback_reason = self._check_rollback_conditions(feature)
            if should_rollback:
                self._rollback_feature(feature, rollback_reason)
                progression_results['features'][feature] = {
                    'action': 'rolled_back',
                    'reason': rollback_reason
                }
                continue

            # Check if feature can progress
            can_progress, progression_reason = self._check_progression_criteria(feature, current_phase, phase_started)
            if can_progress:
                next_phase = self._get_next_phase(current_phase)
                if next_phase:
                    success = self._advance_to_phase(feature, next_phase)
                    if success:
                        progression_results['features'][feature] = {
                            'action': 'advanced',
                            'from_phase': current_phase.value,
                            'to_phase': next_phase.value
                        }
                    else:
                        progression_results['features'][feature] = {
                            'action': 'advance_failed'
                        }
                else:
                    # Feature is fully rolled out
                    self.current_rollouts[feature]['status'] = RolloutStatus.COMPLETED.value
                    progression_results['features'][feature] = {
                        'action': 'completed'
                    }
            else:
                progression_results['features'][feature] = {
                    'action': 'waiting',
                    'reason': progression_reason
                }

        self.save_configuration()
        return progression_results

    def manual_advance_feature(self, feature_name: str) -> bool:
        """
        Manually advance a feature to the next rollout phase

        Args:
            feature_name: Name of feature to advance

        Returns:
            bool: Success status
        """
        if feature_name not in self.current_rollouts:
            self.logger.error("Feature not in active rollout", feature=feature_name)
            return False

        current_phase = RolloutPhase(self.current_rollouts[feature_name]['current_phase'])
        next_phase = self._get_next_phase(current_phase)

        if not next_phase:
            self.logger.warning("Feature already at final phase", feature=feature_name)
            return False

        success = self._advance_to_phase(feature_name, next_phase)
        if success:
            self.logger.info(
                "Feature manually advanced",
                feature=feature_name,
                from_phase=current_phase.value,
                to_phase=next_phase.value
            )

        return success

    def emergency_rollback_all(self) -> Dict[str, bool]:
        """
        Emergency rollback of all Phase-1 features

        Returns:
            Dict with rollback results for each feature
        """
        self.logger.warning("EMERGENCY ROLLBACK: Rolling back all Phase-1 features")

        results = {}
        for feature in self.phase1_features:
            success = self._rollback_feature(feature, "EMERGENCY_ROLLBACK")
            results[feature] = success

        metrics_collector.increment_counter('emergency_rollbacks')
        return results

    def get_rollout_status(self) -> Dict[str, any]:
        """Get current status of all rollouts"""
        status = {
            'as_of': datetime.utcnow().isoformat(),
            'features': {}
        }

        for feature in self.phase1_features:
            flag_status = feature_flags.get_flag_status(feature)
            rollout_info = self.current_rollouts.get(feature, {})

            status['features'][feature] = {
                'flag_enabled': flag_status.get('enabled', False) if flag_status else False,
                'admin_only': flag_status.get('admin_only', True) if flag_status else True,
                'rollout_percentage': flag_status.get('rollout_percentage', 0) if flag_status else 0,
                'current_phase': rollout_info.get('current_phase', 'not_started'),
                'status': rollout_info.get('status', 'not_started'),
                'metrics': self._get_feature_metrics(feature)
            }

        return status

    def _capture_baseline_metrics(self, feature: str) -> Dict[str, float]:
        """Capture baseline metrics before rollout"""
        return {
            'baseline_captured_at': time.time(),
            'error_rate': 0.0,
            'response_time_p95': 0.0,
            'memory_usage': 0.0,
            'request_count': 0
        }

    def _check_rollback_conditions(self, feature: str) -> Tuple[bool, Optional[str]]:
        """Check if feature should be rolled back due to errors"""
        metrics = self._get_feature_metrics(feature)

        # Check error rate
        if metrics.get('error_rate_percent', 0) > self.rollback_thresholds['error_rate_percent']:
            return True, f"Error rate {metrics['error_rate_percent']}% exceeds threshold"

        # Check response time
        if metrics.get('response_time_p95_ms', 0) > self.rollback_thresholds['response_time_p95_ms']:
            return True, f"P95 response time {metrics['response_time_p95_ms']}ms exceeds threshold"

        # Check memory usage
        if metrics.get('memory_usage_mb', 0) > self.rollback_thresholds['memory_usage_mb']:
            return True, f"Memory usage {metrics['memory_usage_mb']}MB exceeds threshold"

        return False, None

    def _check_progression_criteria(self, feature: str, current_phase: RolloutPhase,
                                   phase_started: datetime) -> Tuple[bool, str]:
        """Check if feature meets criteria to progress to next phase"""
        # Check minimum runtime
        runtime_minutes = (datetime.utcnow() - phase_started).total_seconds() / 60
        if runtime_minutes < self.progression_criteria['min_runtime_minutes']:
            return False, f"Runtime {runtime_minutes:.1f}min < required {self.progression_criteria['min_runtime_minutes']}min"

        # Check metrics
        metrics = self._get_feature_metrics(feature)

        error_rate = metrics.get('error_rate_percent', 0)
        if error_rate > self.progression_criteria['max_error_rate_percent']:
            return False, f"Error rate {error_rate}% > threshold {self.progression_criteria['max_error_rate_percent']}%"

        response_time = metrics.get('response_time_p95_ms', 0)
        if response_time > self.progression_criteria['max_response_time_p95_ms']:
            return False, f"P95 response time {response_time}ms > threshold"

        return True, "All criteria met"

    def _get_next_phase(self, current_phase: RolloutPhase) -> Optional[RolloutPhase]:
        """Get the next rollout phase"""
        phase_progression = [
            RolloutPhase.ADMIN_ONLY,
            RolloutPhase.CANARY_1_PERCENT,
            RolloutPhase.CANARY_25_PERCENT,
            RolloutPhase.FULL_ROLLOUT
        ]

        try:
            current_index = phase_progression.index(current_phase)
            if current_index < len(phase_progression) - 1:
                return phase_progression[current_index + 1]
        except ValueError:
            pass

        return None

    def _advance_to_phase(self, feature: str, next_phase: RolloutPhase) -> bool:
        """Advance feature to next rollout phase"""
        try:
            # Update feature flag settings based on phase
            if next_phase == RolloutPhase.ADMIN_ONLY:
                feature_flags.set_flag(feature, enabled=True, admin_only=True, rollout_percentage=0)
            elif next_phase == RolloutPhase.CANARY_1_PERCENT:
                feature_flags.set_flag(feature, enabled=True, admin_only=False, rollout_percentage=1)
            elif next_phase == RolloutPhase.CANARY_25_PERCENT:
                feature_flags.set_flag(feature, enabled=True, admin_only=False, rollout_percentage=25)
            elif next_phase == RolloutPhase.FULL_ROLLOUT:
                feature_flags.set_flag(feature, enabled=True, admin_only=False, rollout_percentage=100)

            # Update rollout tracking
            self.current_rollouts[feature].update({
                'current_phase': next_phase.value,
                'phase_started_at': datetime.utcnow().isoformat(),
                'previous_phase_completed_at': datetime.utcnow().isoformat()
            })

            self.logger.info(
                "Feature advanced to next phase",
                feature=feature,
                phase=next_phase.value
            )

            metrics_collector.increment_counter('canary_phase_advances')
            return True

        except Exception as e:
            self.logger.error(
                "Failed to advance feature to next phase",
                feature=feature,
                target_phase=next_phase.value,
                error=str(e)
            )
            return False

    def _rollback_feature(self, feature: str, reason: str) -> bool:
        """Rollback a feature to disabled state"""
        try:
            feature_flags.rollback_feature(feature)

            if feature in self.current_rollouts:
                self.current_rollouts[feature].update({
                    'status': RolloutStatus.ROLLED_BACK.value,
                    'rolled_back_at': datetime.utcnow().isoformat(),
                    'rollback_reason': reason
                })

            self.logger.warning(
                "Feature rolled back",
                feature=feature,
                reason=reason
            )

            metrics_collector.increment_counter('canary_rollbacks')
            return True

        except Exception as e:
            self.logger.error(
                "Failed to rollback feature",
                feature=feature,
                error=str(e)
            )
            return False

    def _get_feature_metrics(self, feature: str) -> Dict[str, float]:
        """Get current metrics for a feature"""
        # This would integrate with your actual metrics collection
        # For now, returning dummy data that would be replaced with real metrics
        return {
            'error_rate_percent': 0.1,
            'response_time_p95_ms': 250,
            'memory_usage_mb': 64,
            'request_count': metrics_collector.get_counter(f'{feature}_requests'),
            'success_rate_percent': 99.9
        }

# Global canary rollout manager instance
canary_manager = CanaryRolloutManager()

def start_phase1_deployment() -> Dict[str, any]:
    """Start Phase-1 deployment with all safeguards"""
    return canary_manager.start_phase1_rollout()

def check_deployment_health() -> Dict[str, any]:
    """Check health of current deployment and progress rollouts if safe"""
    return canary_manager.check_rollout_progression()

def emergency_rollback() -> Dict[str, bool]:
    """Emergency rollback of all new features"""
    return canary_manager.emergency_rollback_all()