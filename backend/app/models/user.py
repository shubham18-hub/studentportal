from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: Literal["student", "faculty", "admin"]

class UserCreate(UserBase):
    google_id: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    theme_preference: Optional[Literal["light", "dark"]] = None

class User(UserBase):
    id: Optional[str] = None
    google_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    theme_preference: Literal["light", "dark"] = "dark"
    
    class Config:
        from_attributes = True

class UserInDB(User):
    pass
