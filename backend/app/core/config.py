"""
Application Configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "GlobalMart E-Commerce Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/globalmart"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://globalmart.com",
    ]
    
    # Payment Gateways
    PAYMOB_API_KEY: str = os.getenv("PAYMOB_API_KEY", "")
    PAYMOB_INTEGRATION_ID: str = os.getenv("PAYMOB_INTEGRATION_ID", "")
    FAWRY_MERCHANT_CODE: str = os.getenv("FAWRY_MERCHANT_CODE", "")
    FAWRY_SECRET_KEY: str = os.getenv("FAWRY_SECRET_KEY", "")
    
    # Shipping APIs
    BOSTA_API_KEY: str = os.getenv("BOSTA_API_KEY", "")
    ARAMEX_ACCOUNT_NUMBER: str = os.getenv("ARAMEX_ACCOUNT_NUMBER", "")
    ARAMEX_API_KEY: str = os.getenv("ARAMEX_API_KEY", "")
    
    # Third-party Services
    TWILIO_SID: str = os.getenv("TWILIO_SID", "")
    TWILIO_TOKEN: str = os.getenv("TWILIO_TOKEN", "")
    TWILIO_PHONE: str = os.getenv("TWILIO_PHONE", "")
    
    FIREBASE_CREDENTIALS: Optional[str] = os.getenv("FIREBASE_CREDENTIALS", None)
    
    ALIEXPRESS_APP_KEY: str = os.getenv("ALIEXPRESS_APP_KEY", "")
    ALIEXPRESS_SECRET_KEY: str = os.getenv("ALIEXPRESS_SECRET_KEY", "")
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Currency
    DEFAULT_CURRENCY: str = "EGP"
    USD_TO_EGP_RATE: float = 50.0
    PLATFORM_FEE_PERCENTAGE: float = 5.0
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
