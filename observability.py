"""
AtlasNexus Observability System
==============================
Metrics, logging, and monitoring for Phase-1 deployment
"""

import time
import json
import os
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List
import uuid

class MetricsCollector:
    """
    Production-ready metrics collection system
    Tracks all Phase-1 deployment metrics
    """

    def __init__(self):
        self.counters = defaultdict(int)
        self.histograms = defaultdict(list)
        self.gauges = {}
        self.lock = threading.RLock()

        # File storage
        self.metrics_file = '/tmp/metrics.json' if os.environ.get('VERCEL') else 'metrics.json'

        # Initialize Phase-1 specific metrics
        self.init_phase1_metrics()

        # Background thread for metrics persistence
        self.start_metrics_persistence()

    def init_phase1_metrics(self):
        """Initialize Phase-1 specific metric counters"""
        phase1_counters = [
            'permutations_processed_total',
            'gate_a_pruned_count',
            'gate_b_pruned_count',
            'rule_failures_by_key',
            'input_hierarchy_processed',
            'reverse_dscr_calculations',
            'repo_eligibility_checks',
            'viability_tier_assignments',
            'near_miss_captures',
            'error_count_total',
            'request_count_total',
            'security_blocks_total',
            'rate_limit_hits_total'
        ]

        for counter in phase1_counters:
            self.counters[counter] = 0

        # Initialize performance histograms
        self.histograms['p50_step_ms'] = []
        self.histograms['p95_step_ms'] = []
        self.histograms['response_time_ms'] = []
        self.histograms['memory_usage_mb'] = []

    def increment_counter(self, metric_name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with self.lock:
            if labels:
                key = f"{metric_name}_{self._format_labels(labels)}"
            else:
                key = metric_name
            self.counters[key] += value

    def record_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        with self.lock:
            if labels:
                key = f"{metric_name}_{self._format_labels(labels)}"
            else:
                key = metric_name

            # Keep only last 1000 values for memory efficiency
            if len(self.histograms[key]) >= 1000:
                self.histograms[key] = self.histograms[key][-500:]

            self.histograms[key].append({
                'value': value,
                'timestamp': time.time()
            })

    def set_gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        with self.lock:
            if labels:
                key = f"{metric_name}_{self._format_labels(labels)}"
            else:
                key = metric_name
            self.gauges[key] = {
                'value': value,
                'timestamp': time.time()
            }

    def get_counter(self, metric_name: str) -> int:
        """Get counter value"""
        with self.lock:
            return self.counters.get(metric_name, 0)

    def get_histogram_stats(self, metric_name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        with self.lock:
            values = [entry['value'] for entry in self.histograms.get(metric_name, [])]
            if not values:
                return {'count': 0}

            values.sort()
            count = len(values)
            return {
                'count': count,
                'min': values[0],
                'max': values[-1],
                'avg': sum(values) / count,
                'p50': values[int(count * 0.5)] if count > 0 else 0,
                'p90': values[int(count * 0.9)] if count > 0 else 0,
                'p95': values[int(count * 0.95)] if count > 0 else 0,
                'p99': values[int(count * 0.99)] if count > 0 else 0
            }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics for dashboard"""
        with self.lock:
            metrics = {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {}
            }

            for name, values in self.histograms.items():
                metrics['histograms'][name] = self.get_histogram_stats(name)

            return metrics

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for metric names"""
        return '_'.join(f"{k}_{v}" for k, v in sorted(labels.items()))

    def start_metrics_persistence(self):
        """Start background thread for metrics persistence"""
        def persist_metrics():
            while True:
                try:
                    time.sleep(60)  # Persist every minute
                    self.save_metrics()
                except Exception as e:
                    print(f"[METRICS] Error persisting metrics: {e}")

        thread = threading.Thread(target=persist_metrics, daemon=True)
        thread.start()

    def save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.get_all_metrics(), f, indent=2)
        except Exception as e:
            print(f"[METRICS] Error saving metrics: {e}")

class StructuredLogger:
    """
    Structured logging system for Phase-1 deployment
    """

    def __init__(self):
        self.log_file = '/tmp/app_structured.log' if os.environ.get('VERCEL') else 'app_structured.log'

    def log(self, level: str, message: str, permutation_id: str = None, gate: str = None,
            result: str = None, reason: str = None, ruleset_version: str = None,
            seed: str = None, **kwargs):
        """
        Log structured message with Phase-1 specific fields

        Args:
            level: Log level (INFO, WARN, ERROR, DEBUG)
            message: Log message
            permutation_id: Permutation identifier
            gate: Gate identifier (A, B, etc.)
            result: Processing result
            reason: Reason for result
            ruleset_version: Version of ruleset used
            seed: Random seed for reproducibility
            **kwargs: Additional fields
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.upper(),
            'message': message,
            'correlation_id': str(uuid.uuid4())[:8]
        }

        # Add Phase-1 specific fields
        if permutation_id:
            log_entry['permutation_id'] = permutation_id
        if gate:
            log_entry['gate'] = gate
        if result:
            log_entry['result'] = result
        if reason:
            log_entry['reason'] = reason
        if ruleset_version:
            log_entry['ruleset_version'] = ruleset_version
        if seed:
            log_entry['seed'] = seed

        # Add any additional fields
        log_entry.update(kwargs)

        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[LOGGER] Error writing log: {e}")

        # Also print to console in development
        if not os.environ.get('VERCEL_ENV') == 'production':
            print(f"[{level.upper()}] {message} | {log_entry}")

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log('WARN', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log('ERROR', message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if not os.environ.get('VERCEL_ENV') == 'production':
            self.log('DEBUG', message, **kwargs)

class PerformanceTracker:
    """
    Performance tracking for Phase-1 operations
    """

    def __init__(self, metrics_collector: MetricsCollector, logger: StructuredLogger):
        self.metrics = metrics_collector
        self.logger = logger

    def track_operation(self, operation_name: str, permutation_id: str = None):
        """Context manager for tracking operation performance"""
        return OperationTracker(operation_name, permutation_id, self.metrics, self.logger)

class OperationTracker:
    """Context manager for tracking individual operations"""

    def __init__(self, operation_name: str, permutation_id: str, metrics: MetricsCollector, logger: StructuredLogger):
        self.operation_name = operation_name
        self.permutation_id = permutation_id
        self.metrics = metrics
        self.logger = logger
        self.start_time = None
        self.memory_start = None

    def __enter__(self):
        self.start_time = time.time()
        try:
            import psutil
            self.memory_start = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            self.memory_start = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        # Record performance metrics
        self.metrics.record_histogram(f'{self.operation_name}_duration_ms', duration_ms)
        self.metrics.increment_counter(f'{self.operation_name}_total')

        if self.memory_start:
            try:
                import psutil
                memory_end = psutil.Process().memory_info().rss / 1024 / 1024
                memory_delta = memory_end - self.memory_start
                self.metrics.record_histogram('memory_usage_mb', memory_end)
                if memory_delta > 10:  # Log significant memory increases
                    self.logger.warning(f"High memory usage in {self.operation_name}",
                                        memory_delta_mb=memory_delta,
                                        permutation_id=self.permutation_id)
            except ImportError:
                pass

        # Log operation completion
        if exc_type:
            self.metrics.increment_counter(f'{self.operation_name}_errors')
            self.logger.error(f"Operation {self.operation_name} failed",
                              duration_ms=duration_ms,
                              permutation_id=self.permutation_id,
                              error=str(exc_val))
        else:
            self.logger.info(f"Operation {self.operation_name} completed",
                             duration_ms=duration_ms,
                             permutation_id=self.permutation_id)

class DashboardDataProvider:
    """
    Provides data for observability dashboard tiles
    """

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data"""
        metrics = self.metrics.get_all_metrics()

        return {
            'throughput': {
                'title': 'Throughput',
                'permutations_per_minute': self._calculate_rate('permutations_processed_total'),
                'requests_per_minute': self._calculate_rate('request_count_total'),
                'current_load': self._get_current_load()
            },
            'performance': {
                'title': 'Performance',
                'avg_response_time': metrics['histograms'].get('response_time_ms', {}).get('avg', 0),
                'p95_response_time': metrics['histograms'].get('response_time_ms', {}).get('p95', 0),
                'p95_step_time': metrics['histograms'].get('p95_step_ms', {}).get('p95', 0)
            },
            'errors': {
                'title': 'Error Rate',
                'total_errors': metrics['counters'].get('error_count_total', 0),
                'rate_limit_hits': metrics['counters'].get('rate_limit_hits_total', 0),
                'security_blocks': metrics['counters'].get('security_blocks_total', 0),
                'error_rate': self._calculate_error_rate()
            },
            'pruning': {
                'title': 'Pruning Efficiency',
                'gate_a_pruned': metrics['counters'].get('gate_a_pruned_count', 0),
                'gate_b_pruned': metrics['counters'].get('gate_b_pruned_count', 0),
                'pruning_rate': self._calculate_pruning_rate()
            },
            'memory': {
                'title': 'Memory Usage',
                'current_mb': metrics['histograms'].get('memory_usage_mb', {}).get('avg', 0),
                'peak_mb': metrics['histograms'].get('memory_usage_mb', {}).get('max', 0)
            }
        }

    def _calculate_rate(self, counter_name: str) -> float:
        """Calculate rate per minute for a counter"""
        # This is a simplified calculation - in production you'd use time windows
        return self.metrics.get_counter(counter_name) / 60.0  # Assuming 1-minute window

    def _get_current_load(self) -> str:
        """Get current system load status"""
        total_requests = self.metrics.get_counter('request_count_total')
        if total_requests < 100:
            return 'Low'
        elif total_requests < 1000:
            return 'Medium'
        else:
            return 'High'

    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        total_requests = self.metrics.get_counter('request_count_total')
        total_errors = self.metrics.get_counter('error_count_total')
        if total_requests == 0:
            return 0.0
        return (total_errors / total_requests) * 100

    def _calculate_pruning_rate(self) -> float:
        """Calculate pruning efficiency rate"""
        total_processed = self.metrics.get_counter('permutations_processed_total')
        total_pruned = (self.metrics.get_counter('gate_a_pruned_count') +
                        self.metrics.get_counter('gate_b_pruned_count'))
        if total_processed == 0:
            return 0.0
        return (total_pruned / total_processed) * 100

# Global instances
metrics_collector = MetricsCollector()
structured_logger = StructuredLogger()
performance_tracker = PerformanceTracker(metrics_collector, structured_logger)
dashboard_provider = DashboardDataProvider(metrics_collector)