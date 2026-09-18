from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://ecelluser:ecellpass@localhost:27017/ecell?authSource=admin")
    mongodb_pool_size: int = 50  # Connection pool for 1k students
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Admin
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@ecell.com")
    admin_password_hash: str = os.getenv("ADMIN_PASSWORD_HASH", "")
    
    # Email domains
    allowed_domains: List[str] = ["klecba.edu.in", "kle.ac.in", "klecba.edu"]
    
    # CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Privacy & Security
    hash_passwords: bool = True
    enable_https_only: bool = os.getenv("ENVIRONMENT", "development") == "production"
    log_user_pii: bool = False  # Never log personally identifiable information
    
    # Caching
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    enable_redis: bool = os.getenv("ENABLE_REDIS", "false").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()
