from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ==================== AUTHENTICATION MODELS ====================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2)
    
    class Config:
        example = {
            "email": "user@example.com",
            "password": "securepassword123",
            "full_name": "John Doe"
        }


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    
    class Config:
        example = {
            "email": "user@example.com",
            "password": "securepassword123"
        }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str


class UserResponse(BaseModel):
    """User profile response"""
    user_id: str = Field(alias="_id")
    email: str
    full_name: str
    target_role: Optional[str] = "Software Engineer"
    years_of_experience: Optional[int] = 0
    skills: Optional[list] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class ProfileUpdateRequest(BaseModel):
    """Update profile and onboarding preferences"""
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    years_of_experience: Optional[int] = None
    skills: Optional[list] = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    class Config:
        example = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123"
        }

