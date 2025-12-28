"""Application configuration module.

Extends the existing firefly_bill_sync config with FastAPI-specific settings.
"""

import sys
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

# Add parent directory to path for importing firefly_bill_sync
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from firefly_bill_sync.config import Config as BaseConfig


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Settings
    api_title: str = "CoinWise API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Firefly Settings (from parent config)
    firefly_api_url: str = BaseConfig.FIREFLY_API_URL
    firefly_api_token: str = BaseConfig.FIREFLY_API_TOKEN

    # Email Settings
    email_imap_server: str = BaseConfig.EMAIL_IMAP_SERVER

    class Config:
        """Pydantic settings configuration."""

        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
