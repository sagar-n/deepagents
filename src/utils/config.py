"""Configuration management for DeepAgents."""

import os
from typing import Optional


class Settings:
    """Application settings and configuration."""

    # LLM Configuration
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gpt-oss")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))

    # Server Configuration
    SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "7860"))

    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "100"))

    # Rate Limiting
    RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "10"))

    # API Configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_MIN_WAIT: int = int(os.getenv("RETRY_MIN_WAIT", "2"))
    RETRY_MAX_WAIT: int = int(os.getenv("RETRY_MAX_WAIT", "10"))

    # Data Configuration
    DEFAULT_HISTORY_PERIOD: str = os.getenv("DEFAULT_HISTORY_PERIOD", "3mo")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Export
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", "exports")

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        try:
            assert cls.TEMPERATURE >= 0.0 and cls.TEMPERATURE <= 1.0
            assert cls.CACHE_TTL > 0
            assert cls.SERVER_PORT > 0 and cls.SERVER_PORT < 65536
            assert cls.MAX_RETRIES > 0
            return True
        except AssertionError:
            return False


# Global settings instance
settings = Settings()
