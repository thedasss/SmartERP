"""
SmartERP Application Configuration
Reads settings from environment variables / .env file
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env relative to this file's location (backend/app/core/)
# This works regardless of the working directory (backend/, root, etc.)
_ENV_FILE = Path(__file__).parent.parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    app_env: str = "development"
    app_name: str = "SmartERP"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────
    # Default to SQLite for zero-config local development
    database_url: str = "sqlite+aiosqlite:///./smarterp.db"
    database_echo: bool = False

    # ── JWT ──────────────────────────────────────────────────
    jwt_secret: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── Storage ──────────────────────────────────────────────
    storage_backend: str = "local"  # "local" | "azure"
    local_storage_path: str = "./local_storage"

    azure_storage_account: str = ""
    azure_storage_key: str = ""
    azure_container_name: str = "smarterp"

    # ── Qdrant ───────────────────────────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "smarterp_documents"

    # ── LLM / AI ─────────────────────────────────────────────
    llm_provider: str = "ollama"  # "ollama" | "openai" | "google"
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"
    openai_api_key: str = ""
    google_api_key: str = ""

    # ── Logging ──────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"

    # ── Rate Limiting ────────────────────────────────────────
    rate_limit_per_minute: int = 60
    auth_rate_limit_per_minute: int = 10

    # ── Security ─────────────────────────────────────────────
    password_min_length: int = 8
    max_login_attempts: int = 5
    account_lockout_minutes: int = 15

    # ── Seed Data ────────────────────────────────────────────
    seed_admin_email: str = "admin@smarterp.com"
    seed_admin_password: str = "Admin@12345!"
    seed_company_name: str = "SmartERP Demo Company"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
