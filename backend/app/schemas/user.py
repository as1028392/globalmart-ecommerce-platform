"""
User Schemas - Pydantic models for validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """User registration schema"""
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    password: str = Field(..., min_length=8, max_length=255, description="Password (min 8 chars)")
    password_confirm: str = Field(..., description="Password confirmation")
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "Mostafa",
                "phone": "201034804073",
                "password": "As99887766!",
                "password_confirm": "As99887766!"
            }
        }

class UserLogin(BaseModel):
    """User login schema"""
    phone: PhoneStr = Field(..., description="Phone address")
    password: str = Field(..., description="Password")
    
    class Config:
        schema_extra = {
            "example": {
                "phone": "201034804073",
                "password": "As99887766!"
            }
        }

class UserUpdate(BaseModel):
    """User profile update schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "Mostafa",
                "phone": "201034804073"
            }
        }

class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="Email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=255)
    password_confirm: str = Field(..., description="Password confirmation")

class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str = Field(..., description="Verification token from email")

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=86400, description="Token expiration in seconds")

class UserResponse(BaseModel):
    """User response schema (without sensitive data)"""
    id: int
    email: str
    full_name: str
    phone: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "full_name": "Mostafa",
                "phone": "201034804073",
                "is_verified": True,
                "is_active": True,
                "created_at": "2026-06-10T16:00:00Z"
            }
        }

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")
