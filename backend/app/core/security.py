"""
Security Module - Password hashing, JWT tokens, email verification
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import secrets
import string

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    user_id: int
    email: str
    role: str
    exp: datetime

class JWTService:
    """JWT Token management"""
    
    @staticmethod
    def create_access_token(
        user_id: int,
        email: str,
        role: str = "user",
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Generate refresh token (7 days)"""
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = {
            "user_id": user_id,
            "type": "refresh",
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.REFRESH_SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify refresh token"""
        try:
            payload = jwt.decode(
                token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                return None
            return payload
        except JWTError:
            return None

class PasswordService:
    """Password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

class EmailVerificationService:
    """Email verification token generation and validation"""
    
    @staticmethod
    def generate_verification_token(length: int = 32) -> str:
        """Generate random verification token"""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_reset_token(length: int = 32) -> str:
        """Generate password reset token"""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
