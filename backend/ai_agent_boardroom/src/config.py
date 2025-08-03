import os
from typing import Dict, Any


class Config:
    """Configuration management for the AI Agent Boardroom application."""

    # Flask configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "asdf#FGSgvasgf$5$WGT")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///boardroom.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    # Typefully configuration
    TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "1p80KNGogHZnWXYo")

    # X (Twitter) API configuration
    X_API_BASE_URL = os.getenv("X_API_BASE_URL", "https://api.x.com")
    X_API_VERSION = os.getenv("X_API_VERSION", "2")

    # TTS configuration
    TTS_AUDIO_DIR = os.getenv("TTS_AUDIO_DIR", "static/audio")
    TTS_MAX_TEXT_LENGTH = int(os.getenv("TTS_MAX_TEXT_LENGTH", "50000"))

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration based on environment."""
        if cls.DATABASE_URL.startswith("postgresql://"):
            return {
                "SQLALCHEMY_DATABASE_URI": cls.DATABASE_URL,
                "SQLALCHEMY_TRACK_MODIFICATIONS": cls.SQLALCHEMY_TRACK_MODIFICATIONS,
            }
        else:
            # Default to SQLite for local development
            return {
                "SQLALCHEMY_DATABASE_URI": "sqlite:///boardroom.db",
                "SQLALCHEMY_TRACK_MODIFICATIONS": cls.SQLALCHEMY_TRACK_MODIFICATIONS,
            }

    @classmethod
    def validate_required_config(cls) -> Dict[str, bool]:
        """Validate that required configuration values are set."""
        required_configs = {
            "OPENAI_API_KEY": bool(cls.OPENAI_API_KEY),
            "SECRET_KEY": bool(cls.SECRET_KEY),
        }
        return required_configs

    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get a summary of current configuration (without sensitive values)."""
        return {
            "debug": cls.DEBUG,
            "database_type": (
                "postgresql"
                if cls.DATABASE_URL.startswith("postgresql://")
                else "sqlite"
            ),
            "openai_configured": bool(cls.OPENAI_API_KEY),
            "typefully_configured": bool(cls.TYPEFULLY_API_KEY),
            "log_level": cls.LOG_LEVEL,
            "tts_max_text_length": cls.TTS_MAX_TEXT_LENGTH,
        }
