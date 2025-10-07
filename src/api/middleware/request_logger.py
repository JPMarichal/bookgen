"""
Request logging middleware for FastAPI
Implements structured logging for all API requests with correlation IDs
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from src.monitoring.structured_logger import get_structured_logger, set_correlation_id, clear_correlation_id

logger = get_structured_logger(__name__)


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
        
        # Set correlation ID from header or generate new one
        correlation_id = request.headers.get("X-Correlation-ID")
        correlation_id = set_correlation_id(correlation_id)
        
        # Get request details
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        
        # Log incoming request with structured logger
        logger.info(
            f"Request started: {method} {path}",
            client_ip=client_ip,
            method=method,
            path=path,
            query_params=query_params,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful request
            logger.info(
                f"Request completed: {method} {path} - {response.status_code}",
                client_ip=client_ip,
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(round(duration * 1000, 2))
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Clear correlation ID after request
            clear_correlation_id()
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log failed request
            logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                client_ip=client_ip,
                method=method,
                path=path,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            
            # Clear correlation ID
            clear_correlation_id()
            
            # Re-raise the exception
            raise
