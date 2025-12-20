"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/db/contracts.db")
    
    # Vector DB
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/db/chroma")
    
    # LLM
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    default_llm: str = os.getenv("DEFAULT_LLM", "openai")
    
    # Upload settings
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", 52428800))  # 50MB
    upload_dir: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
