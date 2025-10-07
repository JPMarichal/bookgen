"""
Metrics endpoint for Prometheus monitoring
"""
import logging
import psutil
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Response
from src.monitoring.prometheus_metrics import get_metrics_collector, set_gauge

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monitoring"])

# Track application start time
app_start_time = time.time()


def get_system_metrics():
    """Get system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_used": disk.used,
            "disk_percent": disk.percent
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {}


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus-compatible metrics endpoint
    
    Returns application and system metrics in Prometheus exposition format.
    """
    # Get metrics collector
    collector = get_metrics_collector()
    
    # Update system metrics
    uptime = time.time() - app_start_time
    system_metrics = get_system_metrics()
    
    # Set gauge metrics for system resources
    set_gauge("bookgen_uptime_seconds", uptime)
    
    if system_metrics:
        set_gauge("bookgen_cpu_percent", system_metrics.get('cpu_percent', 0))
        set_gauge("bookgen_memory_percent", system_metrics.get('memory_percent', 0))
        set_gauge("bookgen_memory_available_bytes", system_metrics.get('memory_available', 0))
        set_gauge("bookgen_disk_percent", system_metrics.get('disk_percent', 0))
    
    # Update job stats if available
    try:
        from .biographies import jobs
        
        # Count jobs by status
        job_stats = {
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        
        for job in jobs.values():
            status = job.get("status", "unknown").value if hasattr(job.get("status"), "value") else str(job.get("status", "unknown"))
            job_stats[status] = job_stats.get(status, 0) + 1
        
        # Set gauge for each job status
        for status_key, count in job_stats.items():
            set_gauge("bookgen_jobs_total", count, labels={"status": status_key})
        
    except Exception as e:
        logger.warning(f"Could not get job metrics: {e}")
    
    # Build Prometheus format metrics (legacy format for compatibility)
    metrics_lines = [
        "# HELP bookgen_uptime_seconds Application uptime in seconds",
        "# TYPE bookgen_uptime_seconds gauge",
        f"bookgen_uptime_seconds {uptime:.2f}",
        "",
    ]
    
    if system_metrics:
        metrics_lines.extend([
            "# HELP bookgen_cpu_percent CPU usage percentage",
            "# TYPE bookgen_cpu_percent gauge",
            f"bookgen_cpu_percent {system_metrics.get('cpu_percent', 0)}",
            "",
            "# HELP bookgen_memory_percent Memory usage percentage",
            "# TYPE bookgen_memory_percent gauge",
            f"bookgen_memory_percent {system_metrics.get('memory_percent', 0)}",
            "",
            "# HELP bookgen_memory_available_bytes Available memory in bytes",
            "# TYPE bookgen_memory_available_bytes gauge",
            f"bookgen_memory_available_bytes {system_metrics.get('memory_available', 0)}",
            "",
            "# HELP bookgen_disk_percent Disk usage percentage",
            "# TYPE bookgen_disk_percent gauge",
            f"bookgen_disk_percent {system_metrics.get('disk_percent', 0)}",
            "",
        ])
    
    # Add custom metrics from collector
    try:
        custom_metrics = collector.export_prometheus_format()
        if custom_metrics:
            metrics_lines.append(custom_metrics)
    except Exception as e:
        logger.error(f"Error exporting custom metrics: {e}")
    
    return Response(
        content="\n".join(metrics_lines),
        media_type="text/plain; version=0.0.4"
    )
