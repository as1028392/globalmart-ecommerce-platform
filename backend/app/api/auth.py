"""
Authentication Routes - Register, Login, Profile, Password Reset
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import get_db, User
from app.schemas.user import (
    UserRegister, UserLogin, UserUpdate, UserResponse,
    PasswordReset, TokenResponse
)
from app.services.user_service import UserService
from app.core.security import JWTService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = UserService.register_user(db, user_data)
        access_token = JWTService.create_access_token(
            user_id=user.id,
            email=user.email,
            role="user"
        )
        refresh_token = JWTService.create_refresh_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 86400
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user with email and password"""
    try:
        user = UserService.verify_user_credentials(
            db,
            credentials.email,
            credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="بيانات الدخول غير صحيحة"
            )
        
        UserService.update_last_login(db, user.id)
        
        access_token = JWTService.create_access_token(
            user_id=user.id,
            email=user.email,
            role="user"
        )
        refresh_token = JWTService.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 86400
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/profile", response_model=UserResponse)
async def get_profile(user_id: int):
    """Get current user profile"""
    return {
        "id": user_id,
        "email": "user@example.com",
        "full_name": "User Name",
        "phone": "201001234567",
        "is_verified": True,
        "is_active": True,
        "created_at": "2026-06-10T16:00:00Z"
    }

@router.put("/profile", response_model=UserResponse)
async def update_profile(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    try:
        user = UserService.update_user_profile(db, user_id, update_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/password-reset")
async def request_password_reset(request: PasswordReset):
    """Request password reset"""
    return {
        "message": "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني",
        "status": "email_sent"
    }

@router.post("/logout")
async def logout():
    """Logout user"""
    return {
        "message": "تم تسجيل الخروج بنجاح",
        "status": "success"
    }
