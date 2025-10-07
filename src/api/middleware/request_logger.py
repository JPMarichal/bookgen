"""
Request logging middleware for FastAPI
Implements structured logging for all API requests
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of API requests"""
    
    def __init__(self, app: ASGIApp):
        """
        Initialize request logger middleware
        
        Args:
            app: FastAPI application
        """
        super().__init__(app)
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process and log request"""
        
        # Start timing
        start_time = time.time()
        
        # Get request details
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        
        # Log incoming request
        logger.info(
            f"Request started: {method} {path}",
            extra={
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "query_params": query_params,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful request
            logger.info(
                f"Request completed: {method} {path} - {response.status_code}",
                extra={
                    "client_ip": client_ip,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(round(duration * 1000, 2))
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log failed request
            logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                extra={
                    "client_ip": client_ip,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2)
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise
