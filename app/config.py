from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Razorpay Configuration
    razorpay_key_id: str
    razorpay_key_secret: str
    webhook_secret: str
    
    # Database
    database_url: str = "sqlite:///./payments.db"
    
    class Config:
        env_file = ".env"

settings = Settings()