"""
Application Configuration Settings

These settings are used to configure the application and its behavior.
"""

from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings, loaded from environment variables.

    These settings are validated using Pydantic to ensure type safety and correctness.
    """

    # Hayhooks Configuration
    hayhooks_pipelines_dir: Optional[str] = Field(
        default=None,
        description="Directory containing Hayhooks pipelines. Can be an absolute or relative path.",
    )
    hayhooks_host: str = Field(
        default="localhost",
        min_length=1,
        description="The hostname or IP address for the Hayhooks server.",
    )
    hayhooks_port: int = Field(
        default=1416,
        gt=0,
        le=65535,
        description="The network port for the Hayhooks server (1-65535).",
    )

    # Application Behavior
    log: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="The logging level for the application."
    )
    environment: Literal["development", "production", "test"] = Field(
        default="development",
        description="The runtime environment, controlling features like debug info.",
    )

    class ConfigDict:
        """Pydantic model configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance, accessible throughout the application
settings = Settings()
