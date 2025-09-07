"""Configuration settings for the Vendor Background Check App."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY", "dummy_key")
    GOOGLE_CSE_ID: Optional[str] = os.getenv("GOOGLE_CSE_ID", "dummy_cse_id")
    PUBLIC_RECORDS_API_KEY: str = os.getenv("PUBLIC_RECORDS_API_KEY", "dummy_public_records_key")
    
    # App settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    
    # API Settings
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))
    API_RATE_WINDOW: int = int(os.getenv("API_RATE_WINDOW", "60"))  # in seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()
