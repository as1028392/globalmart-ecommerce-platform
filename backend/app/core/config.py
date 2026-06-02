"""
Core configuration for the E-Commerce Platform
Handles environment variables, encryption, and security settings
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "GlobalMart E-Commerce Platform"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:pass@localhost/globalmart", 
        env="DATABASE_URL"
    )

    # Redis (for caching real-time data)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Currency & Pricing
    DEFAULT_CURRENCY: str = "EGP"
    USD_TO_EGP_RATE: float = Field(default=30.90, env="USD_TO_EGP_RATE")
    PLATFORM_MARGIN_PERCENT: float = Field(default=15.0, env="PLATFORM_MARGIN")
    CUSTOM_DUTIES_PERCENT: float = Field(default=10.0, env="CUSTOM_DUTIES")

    # Shipping
    BASE_SHIPPING_COST_USD: float = Field(default=15.0, env="BASE_SHIPPING")
    SHIPPING_PER_KG_USD: float = Field(default=5.0, env="SHIPPING_PER_KG")

    # API Keys (External Services)
    PAYMOB_API_KEY: str = Field(default="", env="PAYMOB_API_KEY")
    PAYMOB_INTEGRATION_ID: str = Field(default="", env="PAYMOB_INTEGRATION_ID")
    FAWRY_MERCHANT_CODE: str = Field(default="", env="FAWRY_MERCHANT_CODE")

    BOSTA_API_KEY: str = Field(default="", env="BOSTA_API_KEY")
    ARAMEX_API_KEY: str = Field(default="", env="ARAMEX_API_KEY")

    TWILIO_SID: str = Field(default="", env="TWILIO_SID")
    TWILIO_TOKEN: str = Field(default="", env="TWILIO_TOKEN")
    TWILIO_PHONE: str = Field(default="", env="TWILIO_PHONE")

    # Supplier APIs
    ALIEXPRESS_APP_KEY: str = Field(default="", env="ALIEXPRESS_APP_KEY")
    ALIEXPRESS_APP_SECRET: str = Field(default="", env="ALIEXPRESS_APP_SECRET")

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = Field(default="", env="FIREBASE_CREDENTIALS")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Encryption setup for sensitive data
encryption_key = os.environ.get("ENCRYPTION_KEY") or Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data before storing in database"""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data from database"""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()
