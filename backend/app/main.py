from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import logging
import sys

from app.config import settings
from app.database import connect_to_mongo, close_mongo
from app.routes import auth, tasks
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    RateLimitMiddleware,
)

# Configure logging - NEVER log PII
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="E-Cell Task Portal API",
    description="API for E-Cell task management and submission (Privacy-focused, 1k+ student capacity)",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# Middleware - Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Middleware - Request Logging (no PII)
app.add_middleware(RequestLoggingMiddleware)

# Middleware - Rate Limiting for 1k students
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Middleware - Gzip compression for bandwidth optimization
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Middleware - CORS (restricted to frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)

# Middleware - Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.render.com", "*.onrender.com"]
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint - no auth required."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "service": "E-Cell Task Portal API"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "E-Cell Task Portal API",
        "docs": "/docs" if settings.environment == "development" else None,
        "version": "1.0.0"
    }

# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request, exc):
    """Handle rate limit exceptions."""
    logger.warning(f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions - don't expose internal details in production."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if settings.environment == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )

# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize on startup.
    
    Does NOT connect to MongoDB at startup. MongoDB connection is deferred until
    the first request that needs it (lazy connection). This allows the app to start
    and pass health checks even if MongoDB is temporarily unavailable.
    
    This matches production best practices where services should start even if
    dependencies are temporarily unavailable.
    """
    logger.info("Starting up E-Cell Task Portal API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"PII Logging: {'DISABLED' if not settings.log_user_pii else 'ENABLED'}")
    logger.info("Rate limiting: ENABLED for 1k+ students")
    logger.info("MongoDB connection: DEFERRED (lazy) - will connect on first request")
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown.
    
    Safely closes MongoDB connection even if it never fully connected.
    """
    logger.info("Shutting down E-Cell Task Portal API")
    try:
        await close_mongo()
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )
