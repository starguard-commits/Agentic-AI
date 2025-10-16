"""
Configuration for Context Decomposition Strategy

Centralized configuration management for all system settings.
"""

import os
from typing import Optional


class Config:
    """
    System configuration settings.

    All settings can be overridden via environment variables.
    """

    # LLM Provider Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Model Selection
    DECOMPOSITION_MODEL: str = os.getenv("DECOMPOSITION_MODEL", "gpt-4")
    EXECUTION_MODEL: str = os.getenv("EXECUTION_MODEL", "gpt-4")
    SYNTHESIS_MODEL: str = os.getenv("SYNTHESIS_MODEL", "gpt-4")

    # Context Limits (tokens)
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "100000"))
    DECOMPOSITION_TRIGGER_THRESHOLD: int = int(
        os.getenv("DECOMPOSITION_TRIGGER_THRESHOLD", "80000")
    )  # Trigger decomposition at 80% of limit

    # Database Settings
    DB_PATH: str = os.getenv("DB_PATH", "context_mesh.db")
    DB_TIMEOUT: int = int(os.getenv("DB_TIMEOUT", "30"))  # seconds

    # Execution Settings
    MAX_PARALLEL_EXECUTIONS: int = int(os.getenv("MAX_PARALLEL_EXECUTIONS", "5"))
    EXECUTION_TIMEOUT: int = int(os.getenv("EXECUTION_TIMEOUT", "60"))  # seconds
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # Label Settings
    LABEL_SIZE_THRESHOLD_KB: float = float(
        os.getenv("LABEL_SIZE_THRESHOLD_KB", "50.0")
    )  # Split labels larger than this
    LABEL_ACCESS_FREQUENCY_THRESHOLD: int = int(
        os.getenv("LABEL_ACCESS_FREQUENCY_THRESHOLD", "5")
    )  # Split if accessed this many times

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")  # If None, log to stdout

    # Development/Debug
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    SAVE_PROMPTS: bool = os.getenv("SAVE_PROMPTS", "False").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration settings.

        Returns:
            True if valid, raises ValueError otherwise

        TODO: Implement validation logic
        - Check API keys are present
        - Validate model names
        - Check numeric ranges
        """
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")

        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")

        # TODO: Add more validation

        return True

    @classmethod
    def to_dict(cls) -> dict:
        """
        Convert config to dictionary (for logging/debugging).

        Returns:
            Dict of all config values (with API keys masked)

        TODO: Implement conversion with key masking
        """
        return {
            "LLM_PROVIDER": cls.LLM_PROVIDER,
            "DECOMPOSITION_MODEL": cls.DECOMPOSITION_MODEL,
            "EXECUTION_MODEL": cls.EXECUTION_MODEL,
            "SYNTHESIS_MODEL": cls.SYNTHESIS_MODEL,
            "MAX_CONTEXT_TOKENS": cls.MAX_CONTEXT_TOKENS,
            "DB_PATH": cls.DB_PATH,
            "DEBUG_MODE": cls.DEBUG_MODE,
            # API keys intentionally excluded
        }


# Create default instance
config = Config()
