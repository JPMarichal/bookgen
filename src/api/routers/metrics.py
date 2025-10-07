"""
Metrics endpoint for Prometheus monitoring
"""
import logging
import psutil
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Response

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
    uptime = time.time() - app_start_time
    system_metrics = get_system_metrics()
    
    # Build Prometheus format metrics
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
    
    # Import job stats if available
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
        
        metrics_lines.extend([
            "# HELP bookgen_jobs_total Total number of jobs by status",
            "# TYPE bookgen_jobs_total gauge",
        ])
        
        for status_key, count in job_stats.items():
            metrics_lines.append(f'bookgen_jobs_total{{status="{status_key}"}} {count}')
        
        metrics_lines.append("")
        
    except Exception as e:
        logger.warning(f"Could not get job metrics: {e}")
    
    return Response(
        content="\n".join(metrics_lines),
        media_type="text/plain; version=0.0.4"
    )
