"""
Rate limiting middleware for FastAPI
Implements IP-based rate limiting
"""
import time
import logging
from typing import Dict, Callable
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests allowed per minute per IP
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> tuple[bool, int]:
        """
        Check if request is allowed for given IP
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Clean up old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_size
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            # Calculate retry after
            oldest_request = min(self.requests[client_ip])
            retry_after = int(self.window_size - (now - oldest_request)) + 1
            return False, retry_after
        
        # Add current request
        self.requests[client_ip].append(now)
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests by IP address"""
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        exempt_paths: list[str] = None
    ):
        """
        Initialize rate limit middleware
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            exempt_paths: List of paths exempt from rate limiting (e.g., /health, /docs)
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request with rate limiting"""
        
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        is_allowed, retry_after = self.rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}. "
                f"Retry after {retry_after} seconds"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        remaining = self.rate_limiter.requests_per_minute - len(
            self.rate_limiter.requests[client_ip]
        )
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        
        return response
