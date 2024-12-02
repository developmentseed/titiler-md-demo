"""API settings."""

from typing import Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    """FASTAPI application settings."""

    name: str = "TiTiler Multidimensional"
    cors_origins: str = "*"
    cors_allow_methods: str = "GET"
    cachecontrol: str = "public, max-age=3600"
    root_path: str = ""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    @field_validator("cors_origins")
    def parse_cors_origin(cls, v):
        """Parse CORS origins."""
        return [origin.strip() for origin in v.split(",")]

    @field_validator("cors_allow_methods")
    def parse_cors_allow_methods(cls, v):
        """Parse CORS allowed methods."""
        return [method.strip().upper() for method in v.split(",")]


class CacheSettings(BaseSettings):
    """Cache settings"""

    # Diskcache Headers settings
    ttl: int = 300  # in seconds
    maxsize: int = 5120000000  # in bytes
    directory: Optional[str] = None

    # Whether or not caching is enabled
    disable: bool = False

    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def check_enable(self):
        """Check if cache is disabled."""
        if self.cache_disable:
            self.cache_headers_ttl = 0
            self.cache_headers_maxsize = 0
            self.cache_blocks_ttl = 0
            self.cache_blocks_maxsize = 0

        return self
