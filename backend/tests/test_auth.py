import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security import get_password_hash, verify_password

client = TestClient(app)

@pytest.mark.auth
class TestAuthentication:
    """Authentication endpoint tests."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "E-Cell Task Portal API" in data["message"]
    
    def test_admin_login_invalid_email(self):
        """Test admin login with wrong email."""
        response = client.post(
            "/api/auth/admin/login",
            json={"email": "wrong@email.com", "password": "password"}
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_admin_login_invalid_password(self):
        """Test admin login with wrong password."""
        response = client.post(
            "/api/auth/admin/login",
            json={"email": "admin@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_token_verification_missing(self):
        """Test API call without token."""
        response = client.get("/api/tasks/admin/all")
        assert response.status_code == 403
    
    def test_token_verification_invalid(self):
        """Test API call with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/tasks/admin/all", headers=headers)
        assert response.status_code == 401
    
    def test_logout_endpoint(self):
        """Test logout endpoint."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

@pytest.mark.auth
class TestPasswordSecurity:
    """Password hashing and security tests."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Hash should be bcrypt format
        assert hashed.startswith("$2b$")
    
    def test_password_verification(self):
        """Test password verification."""
        password = "secure_password_123"
        hashed = get_password_hash(password)
        
        # Correct password should verify
        assert verify_password(password, hashed)
        
        # Wrong password should not verify
        assert not verify_password("wrong_password", hashed)
    
    def test_password_hashing_different_each_time(self):
        """Test that hashing produces different output each time."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify the same password
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
