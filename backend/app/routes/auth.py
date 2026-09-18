from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from app.models.auth import AdminLoginRequest, GoogleAuthRequest, TokenResponse, TokenData
from app.models.user import User, UserCreate
from app.security import (
    create_access_token, 
    verify_password, 
    verify_google_token, 
    is_allowed_domain,
    verify_token,
    get_password_hash
)
from app.config import settings
from app.database import get_db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(request: AdminLoginRequest, db=Depends(get_db)):
    """Login as admin with email and password."""
    # Check if email matches admin email
    if request.email != settings.admin_email:
        logger.warning(f"Admin login attempt with wrong email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(request.password, settings.admin_password_hash):
        logger.warning(f"Admin login attempt with wrong password for: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": request.email, "role": "admin"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": request.email,
            "role": "admin",
            "name": "Administrator"
        }
    }

@router.post("/google", response_model=TokenResponse)
async def google_login(request: GoogleAuthRequest, db=Depends(get_db)):
    """Login with Google OAuth token."""
    # Verify Google token
    try:
        idinfo = verify_google_token(request.id_token)
    except HTTPException:
        raise
    
    email = idinfo.get("email")
    name = idinfo.get("name", "")
    google_id = idinfo.get("sub")
    
    # Check if email domain is allowed
    if not is_allowed_domain(email):
        logger.warning(f"Login attempt with disallowed domain: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email domain not allowed"
        )
    
    # Get or create user in database
    users_collection = db["users"]
    existing_user = await users_collection.find_one({"email": email})
    
    if existing_user:
        user_id = str(existing_user["_id"])
        role = existing_user.get("role", "student")
    else:
        # Create new user (default role is student)
        new_user = {
            "email": email,
            "name": name,
            "google_id": google_id,
            "role": "student",
            "created_at": __import__("datetime").datetime.utcnow(),
            "updated_at": __import__("datetime").datetime.utcnow(),
            "theme_preference": "dark"
        }
        result = await users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        role = "student"
    
    # Create token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": email, "user_id": user_id, "role": role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": email,
            "role": role,
            "name": name,
            "id": user_id
        }
    }

@router.get("/me", response_model=dict)
async def get_current_user(token_data: TokenData = Depends(verify_token), db=Depends(get_db)):
    """Get current authenticated user."""
    if token_data.role == "admin":
        return {
            "email": token_data.email,
            "role": "admin",
            "name": "Administrator"
        }
    
    users_collection = db["users"]
    user = await users_collection.find_one({"_id": ObjectId(token_data.user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user.get("role", "student"),
        "theme_preference": user.get("theme_preference", "dark")
    }

@router.post("/logout")
async def logout():
    """Logout - client should discard token."""
    return {"message": "Logged out successfully"}
