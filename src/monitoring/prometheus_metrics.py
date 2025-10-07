"""
Prometheus metrics collection for BookGen application
Implements comprehensive metrics tracking for monitoring and observability
"""
import time
import functools
from typing import Callable, Dict, Any, Optional
from collections import defaultdict
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Centralized metrics collector for Prometheus
    Tracks counters, gauges, histograms, and summaries
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self._metrics_lock = Lock()
        
        # Counters - monotonically increasing values
        self._counters = defaultdict(float)
        
        # Gauges - values that can go up and down
        self._gauges = defaultdict(float)
        
        # Histograms - observations bucketed by value
        self._histograms = defaultdict(list)
        
        # Labels for metrics
        self._labels = defaultdict(dict)
        
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric
        
        Args:
            name: Metric name
            value: Increment value (default 1.0)
            labels: Optional labels for the metric
        """
        with self._metrics_lock:
            label_key = self._get_label_key(labels)
            full_name = f"{name}{label_key}"
            self._counters[full_name] += value
            if labels:
                self._labels[full_name] = labels
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric value
        
        Args:
            name: Metric name
            value: Gauge value
            labels: Optional labels for the metric
        """
        with self._metrics_lock:
            label_key = self._get_label_key(labels)
            full_name = f"{name}{label_key}"
            self._gauges[full_name] = value
            if labels:
                self._labels[full_name] = labels
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Add an observation to a histogram
        
        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels for the metric
        """
        with self._metrics_lock:
            label_key = self._get_label_key(labels)
            full_name = f"{name}{label_key}"
            self._histograms[full_name].append(value)
            if labels:
                self._labels[full_name] = labels
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value"""
        label_key = self._get_label_key(labels)
        full_name = f"{name}{label_key}"
        return self._counters.get(full_name, 0.0)
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value"""
        label_key = self._get_label_key(labels)
        full_name = f"{name}{label_key}"
        return self._gauges.get(full_name, 0.0)
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Calculate histogram statistics"""
        label_key = self._get_label_key(labels)
        full_name = f"{name}{label_key}"
        values = self._histograms.get(full_name, [])
        
        if not values:
            return {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }
    
    def export_prometheus_format(self) -> str:
        """
        Export all metrics in Prometheus exposition format
        
        Returns:
            String with metrics in Prometheus format
        """
        lines = []
        
        # Export counters
        for name, value in sorted(self._counters.items()):
            base_name = name.split('{')[0]
            labels = self._labels.get(name, {})
            label_str = self._format_labels(labels)
            
            if base_name not in [line.split()[0] for line in lines if line.startswith("# TYPE")]:
                lines.append(f"# TYPE {base_name} counter")
            
            lines.append(f"{base_name}{label_str} {value}")
        
        # Export gauges
        for name, value in sorted(self._gauges.items()):
            base_name = name.split('{')[0]
            labels = self._labels.get(name, {})
            label_str = self._format_labels(labels)
            
            if base_name not in [line.split()[0] for line in lines if line.startswith("# TYPE")]:
                lines.append(f"# TYPE {base_name} gauge")
            
            lines.append(f"{base_name}{label_str} {value}")
        
        # Export histograms
        for name, values in sorted(self._histograms.items()):
            base_name = name.split('{')[0]
            labels = self._labels.get(name, {})
            stats = self.get_histogram_stats(base_name, labels)
            label_str = self._format_labels(labels)
            
            if base_name not in [line.split()[0] for line in lines if line.startswith("# TYPE")]:
                lines.append(f"# TYPE {base_name} histogram")
            
            lines.append(f"{base_name}_count{label_str} {stats['count']}")
            lines.append(f"{base_name}_sum{label_str} {stats['sum']}")
        
        return "\n".join(lines) + "\n"
    
    @staticmethod
    def _get_label_key(labels: Optional[Dict[str, str]]) -> str:
        """Generate unique key for labels"""
        if not labels:
            return ""
        return "{" + ",".join(f"{k}={v}" for k, v in sorted(labels.items())) + "}"
    
    @staticmethod
    def _format_labels(labels: Dict[str, str]) -> str:
        """Format labels for Prometheus"""
        if not labels:
            return ""
        return "{" + ",".join(f'{k}="{v}"' for k, v in sorted(labels.items())) + "}"
    
    def reset(self):
        """Reset all metrics (useful for testing)"""
        with self._metrics_lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._labels.clear()


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return _metrics_collector


# Convenience functions for common operations

def increment_counter(name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
    """Increment a counter metric"""
    _metrics_collector.increment_counter(name, value, labels)


def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Set a gauge metric"""
    _metrics_collector.set_gauge(name, value, labels)


def observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Observe a value in a histogram"""
    _metrics_collector.observe_histogram(name, value, labels)


# Decorators for tracking

def track_generation_time(func: Callable) -> Callable:
    """
    Decorator to track biography generation time
    
    Usage:
        @track_generation_time
        async def generate_biography(...):
            ...
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Track generation time
            observe_histogram(
                "bookgen_biography_generation_seconds",
                duration,
                labels={"status": "success"}
            )
            increment_counter(
                "bookgen_biography_generation_total",
                labels={"status": "success"}
            )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            
            # Track failed generation
            observe_histogram(
                "bookgen_biography_generation_seconds",
                duration,
                labels={"status": "error"}
            )
            increment_counter(
                "bookgen_biography_generation_total",
                labels={"status": "error"}
            )
            
            raise
    
    return wrapper


def track_api_request(endpoint: str):
    """
    Decorator to track API request metrics
    
    Usage:
        @track_api_request("/api/v1/biographies")
        async def create_biography(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track successful request
                observe_histogram(
                    "bookgen_api_request_duration_seconds",
                    duration,
                    labels={"endpoint": endpoint, "status": "2xx"}
                )
                increment_counter(
                    "bookgen_api_requests_total",
                    labels={"endpoint": endpoint, "status": "2xx"}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Track failed request
                observe_histogram(
                    "bookgen_api_request_duration_seconds",
                    duration,
                    labels={"endpoint": endpoint, "status": "5xx"}
                )
                increment_counter(
                    "bookgen_api_requests_total",
                    labels={"endpoint": endpoint, "status": "5xx"}
                )
                
                raise
        
        return wrapper
    return decorator


def track_error(error_type: str, component: str):
    """
    Track an error occurrence
    
    Args:
        error_type: Type of error (e.g., "validation_error", "api_error")
        component: Component where error occurred (e.g., "source_validation", "content_generation")
    """
    increment_counter(
        "bookgen_errors_total",
        labels={"error_type": error_type, "component": component}
    )
