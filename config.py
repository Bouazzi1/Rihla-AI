"""
Rihla-AI — Configuration centralisée
Pydantic BaseSettings charge automatiquement les variables depuis .env
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Configuration principale de l'application Rihla-AI."""

    # ── PostgreSQL ──
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/rihla_ai",
        description="URL de connexion PostgreSQL async"
    )

    # ── Ollama ──
    OLLAMA_HOST: str = Field(default="http://localhost:11434")
    LLM_MODEL: str = Field(default="llama3.2:3b")
    EMBED_MODEL: str = Field(default="nomic-embed-text")

    # ── WAHA (WhatsApp) ──
    WAHA_URL: str = Field(default="http://localhost:3000")

    # ── n8n ──
    N8N_URL: str = Field(default="http://localhost:5678")

    # ── ChromaDB ──
    CHROMA_PATH: str = Field(default="./data/chroma_db")

    # ── Email (Mailhog) ──
    SMTP_HOST: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=1025)

    # ── Redis ──
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # ── App ──
    APP_NAME: str = Field(default="Rihla-AI")
    DEBUG: bool = Field(default=True)

    # ── Chemins ──
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent)

    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "data"

    @property
    def UPLOADS_DIR(self) -> Path:
        return self.BASE_DIR / "data" / "uploads"

    @property
    def KNOWLEDGE_DIR(self) -> Path:
        return self.BASE_DIR / "data" / "knowledge_base"

    @property
    def PROGRAMMES_DIR(self) -> Path:
        return self.BASE_DIR / "data" / "programmes"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Instance singleton
settings = Settings()
