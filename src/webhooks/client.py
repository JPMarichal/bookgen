"""
Webhook client for sending notifications to external systems
"""
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


class WebhookClient:
    """
    Client for sending webhook notifications to external URLs
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize webhook client
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        retry_count: int = 0
    ) -> tuple[bool, Optional[str]]:
        """
        Send webhook POST request
        
        Args:
            url: Webhook URL
            payload: Data to send
            headers: Optional custom headers
            retry_count: Current retry attempt
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "BookGen-Webhook/1.0"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers=default_headers
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook sent successfully to {url}: {response.status_code}")
                return True, None
            else:
                error_msg = f"Webhook failed with status {response.status_code}: {response.text[:200]}"
                logger.warning(error_msg)
                
                # Retry on 5xx errors
                if response.status_code >= 500 and retry_count < self.max_retries:
                    logger.info(f"Retrying webhook to {url} (attempt {retry_count + 1}/{self.max_retries})")
                    return await self.send_webhook(url, payload, headers, retry_count + 1)
                
                return False, error_msg
        
        except httpx.TimeoutException as e:
            error_msg = f"Webhook timeout to {url}: {str(e)}"
            logger.error(error_msg)
            
            if retry_count < self.max_retries:
                logger.info(f"Retrying webhook to {url} (attempt {retry_count + 1}/{self.max_retries})")
                return await self.send_webhook(url, payload, headers, retry_count + 1)
            
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Webhook error to {url}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    async def send_completion_notification(
        self,
        webhook_url: str,
        job_id: str,
        biography_id: int,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send job completion webhook
        
        Args:
            webhook_url: Target webhook URL
            job_id: Job identifier
            biography_id: Biography ID
            status: Job status (completed, failed)
            metadata: Optional additional metadata
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        payload = {
            "event": "job.completed",
            "job_id": job_id,
            "biography_id": biography_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        return await self.send_webhook(webhook_url, payload)
    
    async def send_progress_update(
        self,
        webhook_url: str,
        job_id: str,
        progress: float,
        phase: str,
        message: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send progress update webhook
        
        Args:
            webhook_url: Target webhook URL
            job_id: Job identifier
            progress: Progress percentage (0-100)
            phase: Current phase
            message: Optional message
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        payload = {
            "event": "job.progress",
            "job_id": job_id,
            "progress": progress,
            "phase": phase,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return await self.send_webhook(webhook_url, payload)
    
    async def send_error_alert(
        self,
        webhook_url: str,
        job_id: str,
        error: str,
        severity: str = "error"
    ) -> tuple[bool, Optional[str]]:
        """
        Send error alert webhook
        
        Args:
            webhook_url: Target webhook URL
            job_id: Job identifier
            error: Error message
            severity: Error severity
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        payload = {
            "event": "job.error",
            "job_id": job_id,
            "error": error,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return await self.send_webhook(webhook_url, payload)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception:
            pass
