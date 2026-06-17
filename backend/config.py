"""
config.py — Secure configuration loader.

All secrets are resolved from environment variables.
No literal fallback values are used for secrets to prevent accidental exposure.
If critical secrets are missing in production, the app will fail fast.
"""

import os
import secrets
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Database ──────────────────────────────────────────────────────────────────
# Defaults to a local SQLite demo database. Override with a real connection
# string for Postgres/MySQL (e.g. postgresql+asyncpg://user:pass@host/db).
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:///./demo.db"
)

# Synchronous URL for schema introspection (SQLite only)
DATABASE_SYNC_URL: str = DATABASE_URL.replace(
    "sqlite+aiosqlite", "sqlite"
).replace("postgresql+asyncpg", "postgresql+psycopg2")

# ── LLM API Keys ─────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
HUGGINGFACE_API_KEY: str = os.environ.get("HUGGINGFACE_API_KEY", os.environ.get("HF_TOKEN", ""))

LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "google")  # "google" | "openai" | "huggingface"
LLM_MODEL: str = os.environ.get("LLM_MODEL", "gemini-1.5-flash")

if LLM_PROVIDER == "huggingface" and LLM_MODEL == "gemini-1.5-flash":
    LLM_MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"

HF_INJECTION_MODEL: str = os.environ.get(
    "HF_INJECTION_MODEL", "protectai/deberta-v3-base-prompt-injection-v2"
)
HF_SUMMARY_MODEL: str = os.environ.get(
    "HF_SUMMARY_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"
)

# ── Backend API Key ───────────────────────────────────────────────────────────
# TODO(security): In production, replace with a proper OAuth 2.0 / OIDC provider.
# Resolution order: env var → local file → ephemeral random (dev only)
def _resolve_api_key() -> str:
    if val := os.environ.get("API_SECRET_KEY"):
        return val
    key_file = Path("api_secret.key")
    if key_file.exists():
        return key_file.read_text().strip()
    # Dev-only ephemeral key — NOT suitable for horizontal scaling
    ephemeral = secrets.token_urlsafe(32)
    logger.warning(
        "WARNING: API_SECRET_KEY not set. Generated ephemeral key (dev only): %s\n"
        "   This key is instance-isolated and resets on every restart.",
        ephemeral,
    )
    return ephemeral


API_SECRET_KEY: str = _resolve_api_key()

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS: list[str] = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

# ── Rate Limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30"))

# ── Agent Settings ────────────────────────────────────────────────────────────
MAX_RETRIES: int = int(os.environ.get("MAX_RETRIES", "3"))
MAX_ROWS: int = int(os.environ.get("MAX_ROWS", "1000"))  # Hard cap on SQL result rows

# ── Validate critical settings ────────────────────────────────────────────────
def validate() -> None:
    """Called at startup to ensure the app is correctly configured."""
    if LLM_PROVIDER == "google" and not GOOGLE_API_KEY:
        raise EnvironmentError(
            "GOOGLE_API_KEY is required when LLM_PROVIDER='google'. "
            "Set it in your .env file."
        )
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise EnvironmentError(
                "OPENAI_API_KEY is required when LLM_PROVIDER='openai'. "
                "Set it in your .env file."
            )
        logger.warning(
            "OpenAI provider selected. Ensure you have installed: "
            "pip install 'langchain-openai>=0.2.0'"
        )
    if LLM_PROVIDER == "huggingface" and not HUGGINGFACE_API_KEY:
        raise EnvironmentError(
            "HUGGINGFACE_API_KEY (or HF_TOKEN) is required when LLM_PROVIDER='huggingface'. "
            "Set it in your .env file."
        )
