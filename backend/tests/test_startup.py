"""
Simple startup test to verify the backend can initialize without errors.
This catches import issues and configuration problems early.
"""

import pytest
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_app_imports():
    """Test that all app modules can be imported without errors."""
    from app.main import app
    assert app is not None
    assert app.title == "E-Cell Task Portal API"


def test_app_has_health_endpoint():
    """Test that health endpoint is registered."""
    from app.main import app
    routes = [route.path for route in app.routes]
    assert "/health" in routes


def test_app_has_root_endpoint():
    """Test that root endpoint is registered."""
    from app.main import app
    routes = [route.path for route in app.routes]
    assert "/" in routes


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test that health endpoint responds correctly."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "service" in data


def test_config_loads():
    """Test that configuration loads without errors."""
    from app.config import settings
    assert settings is not None
    assert settings.environment in ["development", "production"]
    assert settings.algorithm == "HS256"


def test_middleware_imports():
    """Test that all middleware can be imported."""
    from app.middleware.security import (
        SecurityHeadersMiddleware,
        RequestLoggingMiddleware,
        RateLimitMiddleware,
    )
    assert SecurityHeadersMiddleware is not None
    assert RequestLoggingMiddleware is not None
    assert RateLimitMiddleware is not None


def test_routes_import():
    """Test that all route modules can be imported."""
    from app.routes import auth, tasks
    assert auth is not None
    assert tasks is not None
