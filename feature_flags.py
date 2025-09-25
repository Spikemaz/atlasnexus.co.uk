"""
AtlasNexus Feature Flag System
============================
Centralized feature flag management with canary rollout support
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import threading

class FeatureFlagManager:
    """
    Production-ready feature flag system with:
    - Admin-only flags for new features
    - Canary rollout percentages
    - User-based targeting
    - Rollback capabilities
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or '/tmp/feature_flags.json' if os.environ.get('VERCEL') else 'feature_flags.json'
        self.flags = {}
        self.lock = threading.RLock()
        self.load_flags()

    def load_flags(self):
        """Load feature flags from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.flags = json.load(f)
            else:
                self.flags = self.get_default_flags()
                self.save_flags()
        except Exception as e:
            print(f"[FEATURE_FLAGS] Error loading flags: {e}")
            self.flags = self.get_default_flags()

    def save_flags(self):
        """Save feature flags to configuration file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.flags, f, indent=2, default=str)
        except Exception as e:
            print(f"[FEATURE_FLAGS] Error saving flags: {e}")

    def get_default_flags(self) -> Dict[str, Any]:
        """Get default feature flags for Phase-1 deployment"""
        return {
            # Existing stable features
            "securitization_engine": {
                "enabled": True,
                "admin_only": True,
                "rollout_percentage": 100,
                "description": "Existing securitization engine"
            },
            "market_news": {
                "enabled": True,
                "admin_only": False,
                "rollout_percentage": 100,
                "description": "Market news service"
            },

            # Phase-1 Core Feature (MUST BE ENABLED)
            "phase1_core": {
                "enabled": True,
                "admin_only": False,
                "rollout_percentage": 100,
                "description": "Phase-1 securitization engine core functionality",
                "implementation_ready": True
            },

            # Phase-1 Week-1 Features (ADMIN-ONLY)
            "input_hierarchy_processor": {
                "enabled": False,
                "admin_only": True,
                "rollout_percentage": 0,
                "description": "Manual → Min/Max → Variations input hierarchy processor",
                "implementation_ready": False
            },
            "reverse_dscr_engine": {
                "enabled": False,
                "admin_only": True,
                "rollout_percentage": 0,
                "description": "Reverse DSCR calculation engine with unit tests",
                "implementation_ready": False
            },
            "repo_eligibility_rules": {
                "enabled": False,
                "admin_only": True,
                "rollout_percentage": 0,
                "description": "UK/EU/US repo eligibility rule tables",
                "implementation_ready": False
            },
            "viability_tiering": {
                "enabled": False,
                "admin_only": True,
                "rollout_percentage": 0,
                "description": "Not Viable → Diamond tiering with near-miss capture",
                "implementation_ready": False
            },

            # Observability features
            "enhanced_logging": {
                "enabled": True,
                "admin_only": True,
                "rollout_percentage": 100,
                "description": "Enhanced structured logging with permutation tracking"
            },
            "performance_metrics": {
                "enabled": True,
                "admin_only": True,
                "rollout_percentage": 100,
                "description": "Performance counters and metrics collection"
            },
            "dashboard_tiles": {
                "enabled": False,
                "admin_only": True,
                "rollout_percentage": 0,
                "description": "Real-time dashboard tiles for throughput and errors",
                "implementation_ready": False
            },

            # Security hardening
            "enhanced_rate_limiting": {
                "enabled": True,
                "admin_only": False,
                "rollout_percentage": 100,
                "description": "Enhanced rate limiting and DDoS protection"
            },
            "input_validation_v2": {
                "enabled": True,
                "admin_only": False,
                "rollout_percentage": 100,
                "description": "Enhanced input validation and sanitization"
            },
            "cors_security": {
                "enabled": True,
                "admin_only": False,
                "rollout_percentage": 100,
                "description": "Enhanced CORS security configuration"
            }
        }

    def is_enabled(self, flag_name: str, user_email: Optional[str] = None, is_admin: bool = False) -> bool:
        """
        Check if a feature flag is enabled for the given user

        Args:
            flag_name: Name of the feature flag
            user_email: Email of the user (for percentage rollouts)
            is_admin: Whether the user is an admin

        Returns:
            bool: True if feature is enabled for this user
        """
        with self.lock:
            flag = self.flags.get(flag_name, {})

            # Feature doesn't exist or is disabled
            if not flag.get('enabled', False):
                return False

            # Admin-only features
            if flag.get('admin_only', False) and not is_admin:
                return False

            # Check rollout percentage
            rollout_percentage = flag.get('rollout_percentage', 0)
            if rollout_percentage == 0:
                return False
            elif rollout_percentage == 100:
                return True

            # Percentage-based rollout using user email hash
            if user_email:
                import hashlib
                hash_value = int(hashlib.md5(f"{flag_name}:{user_email}".encode()).hexdigest()[:8], 16)
                user_percentage = hash_value % 100
                return user_percentage < rollout_percentage

            # No user context, default to disabled for percentage rollouts
            return False

    def set_flag(self, flag_name: str, enabled: bool = True, admin_only: bool = None,
                 rollout_percentage: int = None, description: str = None):
        """Update a feature flag"""
        with self.lock:
            if flag_name not in self.flags:
                self.flags[flag_name] = {}

            flag = self.flags[flag_name]
            flag['enabled'] = enabled
            flag['last_updated'] = datetime.utcnow().isoformat()

            if admin_only is not None:
                flag['admin_only'] = admin_only
            if rollout_percentage is not None:
                flag['rollout_percentage'] = rollout_percentage
            if description is not None:
                flag['description'] = description

            self.save_flags()

    def enable_canary_rollout(self, flag_name: str, initial_percentage: int = 1):
        """Start canary rollout for a feature"""
        with self.lock:
            if flag_name in self.flags:
                self.flags[flag_name]['enabled'] = True
                self.flags[flag_name]['rollout_percentage'] = initial_percentage
                self.flags[flag_name]['canary_started'] = datetime.utcnow().isoformat()
                self.save_flags()
                return True
            return False

    def increase_rollout(self, flag_name: str, new_percentage: int):
        """Increase rollout percentage for a feature"""
        with self.lock:
            if flag_name in self.flags and 0 <= new_percentage <= 100:
                self.flags[flag_name]['rollout_percentage'] = new_percentage
                self.flags[flag_name]['rollout_increased'] = datetime.utcnow().isoformat()
                self.save_flags()
                return True
            return False

    def rollback_feature(self, flag_name: str):
        """Emergency rollback of a feature"""
        with self.lock:
            if flag_name in self.flags:
                self.flags[flag_name]['enabled'] = False
                self.flags[flag_name]['rollback_time'] = datetime.utcnow().isoformat()
                self.save_flags()
                return True
            return False

    def get_all_flags(self) -> Dict[str, Any]:
        """Get all feature flags (admin view)"""
        with self.lock:
            return self.flags.copy()

    def get_flag_status(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific flag"""
        with self.lock:
            return self.flags.get(flag_name)

# Global feature flag manager instance
feature_flags = FeatureFlagManager()

def is_feature_enabled(flag_name: str, user_email: Optional[str] = None, is_admin: bool = False) -> bool:
    """Convenience function to check feature flags"""
    return feature_flags.is_enabled(flag_name, user_email, is_admin)