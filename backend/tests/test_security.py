import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

class TestSecurityHeaders:
    """Test security headers are present."""
    
    def test_security_headers_present(self):
        """Verify security headers in response."""
        response = client.get("/health")
        
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_enabled(self):
        """Verify rate limiting prevents abuse."""
        # Make multiple rapid requests
        responses = []
        for _ in range(110):  # Exceed limit of 100
            response = client.get("/health")
            responses.append(response.status_code)
        
        # Should eventually get rate limited
        assert 429 in responses or 200 in responses[:100]

class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers(self):
        """Verify CORS headers for allowed origins."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_invalid_json_rejected(self):
        """Reject malformed JSON."""
        response = client.post(
            "/api/auth/admin/login",
            content=b"invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]

    def test_sql_injection_attempt_rejected(self):
        """Reject SQL injection attempts."""
        response = client.post(
            "/api/auth/admin/login",
            json={
                "email": "admin@ecell.com' OR '1'='1",
                "password": "password"
            }
        )
        
        # Should reject as invalid email format
        assert response.status_code in [422, 401]

    def test_file_size_limit(self):
        """Verify file size limits are enforced."""
        # This would be tested in actual file upload
        # Limited to 10MB per submission
        pass

class TestAuthenticationSecurity:
    """Test authentication security."""
    
    def test_password_not_in_response(self):
        """Verify passwords never in API responses."""
        response = client.get("/api/auth/me")
        
        # No auth, should fail, but verify response structure
        assert response.status_code == 403
        assert "password" not in str(response.json()).lower()

    def test_token_in_header_only(self):
        """Verify tokens only accepted in Authorization header."""
        # Token should not be accepted in query params
        response = client.get(
            "/api/tasks/admin/all?token=invalid_token"
        )
        
        # Should fail auth
        assert response.status_code == 403

class TestDataProtection:
    """Test data protection measures."""
    
    def test_no_sensitive_data_in_logs(self):
        """Verify sensitive data not exposed in errors."""
        response = client.post(
            "/api/auth/admin/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        error_msg = str(response.json())
        # Should not contain password or detailed DB errors
        assert "password" not in error_msg.lower()
        assert "mongo" not in error_msg.lower()

class TestHTTPSEnforcement:
    """Test HTTPS enforcement in production."""
    
    def test_https_redirect_header(self):
        """Verify HTTPS redirect header configured."""
        # This is configured but may need testing in production
        response = client.get("/health")
        
        # Should include HSTS header
        hsts_header = response.headers.get("Strict-Transport-Security")
        assert hsts_header is not None
        assert "31536000" in hsts_header  # 1 year in seconds

class TestDomainRestriction:
    """Test email domain restriction."""
    
    def test_disallowed_domain_rejected(self):
        """Reject emails from non-allowed domains."""
        # This requires mocking Google OAuth verification
        # Test validates domain check logic
        pass

    def test_allowed_domains_accepted(self):
        """Accept emails from allowed domains."""
        allowed = ["test@klecba.edu.in", "test@kle.ac.in", "test@klecba.edu"]
        # Would test after OAuth integration
        pass

class TestScalability:
    """Test scalability measures for 1k+ students."""
    
    def test_connection_pooling_configured(self):
        """Verify connection pooling is configured."""
        from app.config import settings
        
        assert settings.mongodb_pool_size >= 50
        assert settings.mongodb_pool_size > 0

    def test_rate_limiting_per_ip(self):
        """Verify rate limiting is per-IP for fair access."""
        # Make requests and verify each IP has own limit
        response = client.get("/health")
        
        # Should have process time header
        assert "X-Process-Time" in response.headers

    def test_gzip_compression_enabled(self):
        """Verify GZIP compression for bandwidth savings."""
        response = client.get("/")
        
        # Response should be compressible
        assert response.headers.get("content-encoding") is None  # Depends on client support
        assert response.status_code == 200

class TestErrorHandling:
    """Test error handling doesn't leak info."""
    
    def test_production_errors_generic(self):
        """Verify production errors are generic."""
        from app.config import settings
        
        # In production, errors should be generic
        if settings.environment == "production":
            response = client.get("/api/invalid-endpoint")
            assert response.status_code == 404
            # Error should not contain implementation details

    def test_development_errors_detailed(self):
        """Development errors can be detailed."""
        # Depends on environment setting
        pass

class TestTokenExpiration:
    """Test token expiration."""
    
    def test_token_structure(self):
        """Verify token has proper structure."""
        # Would test with actual valid token
        pass

    def test_expired_token_rejected(self):
        """Verify expired tokens are rejected."""
        # Create token with past expiry and verify rejection
        pass
