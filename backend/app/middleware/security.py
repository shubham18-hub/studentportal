from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log requests (without PII) for monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Don't log sensitive endpoints
        if request.url.path not in ["/api/auth/admin/login", "/api/auth/google"]:
            logger.debug(f"{request.method} {request.url.path}")
        
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for protecting against abuse."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Check rate limit
        current_time = time.time()
        key = client_ip
        
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        # Clean old entries (older than 1 minute)
        self.request_counts[key] = [
            timestamp for timestamp in self.request_counts[key]
            if current_time - timestamp < 60
        ]
        
        # Check if exceeded limit
        if len(self.request_counts[key]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
        
        # Add current request
        self.request_counts[key].append(current_time)
        
        # Cleanup old entries from dict occasionally
        if len(self.request_counts) > 10000:
            self.request_counts.clear()
        
        return await call_next(request)
