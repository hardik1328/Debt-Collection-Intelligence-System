from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # API
    api_title: str = "Contract Intelligence API"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready Contract Intelligence and Risk Audit System"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/db/contracts.db")
    
    # File Storage
    upload_dir: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB
    allowed_extensions: list = ["pdf"]
    
    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, local
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
    
    # Embedding Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dim: int = 384
    
    # Vector Store
    vector_store_type: str = os.getenv("VECTOR_STORE_TYPE", "chromadb")
    chromadb_dir: str = os.getenv("CHROMADB_DIR", "./data/chroma")
    
    # Webhook Configuration
    webhook_timeout: int = 30
    webhook_retries: int = 3
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
