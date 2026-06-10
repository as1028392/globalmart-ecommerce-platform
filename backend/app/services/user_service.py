"""
User Services - Business logic for user management
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models import User
from app.core.security import PasswordService, JWTService, EmailVerificationService
from app.schemas.user import UserRegister, UserUpdate, UserResponse

class UserService:
    """User management service"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.phone == user_data.phone)
        ).first()
        
        if existing_user:
            raise ValueError("البريد الإلكتروني أو رقم الهاتف موجود بالفعل")
        
        # Validate passwords match
        if user_data.password != user_data.password_confirm:
            raise ValueError("كلمات المرور غير متطابقة")
        
        # Create new user
        user = User(
            email=user_data.email,
            phone=user_data.phone,
            full_name=user_data.full_name,
            password_hash=PasswordService.hash_password(user_data.password),
            is_verified=False,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def verify_user_credentials(db: Session, email: str, password: str) -> Optional[User]:
        """Verify user email and password"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not PasswordService.verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            raise ValueError("الحساب معطل")
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user_profile(db: Session, user_id: int, update_data: UserUpdate) -> User:
        """Update user profile"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("المستخدم غير موجود")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def reset_password_request(db: Session, email: str) -> str:
        """Generate password reset token"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists for security
            return EmailVerificationService.generate_reset_token()
        
        reset_token = EmailVerificationService.generate_reset_token()
        # In production, save token with expiration to database
        # For now, we'll just return it
        
        return reset_token
    
    @staticmethod
    def reset_password_confirm(
        db: Session,
        user_id: int,
        new_password: str,
        password_confirm: str
    ) -> User:
        """Confirm password reset"""
        if new_password != password_confirm:
            raise ValueError("كلمات المرور غير متطابقة")
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("المستخدم غير موجود")
        
        user.password_hash = PasswordService.hash_password(new_password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def verify_email(db: Session, user_id: int) -> User:
        """Mark user email as verified"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("المستخدم غير موجود")
        
        user.is_verified = True
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            user.last_login = datetime.utcnow()
            db.add(user)
            db.commit()
