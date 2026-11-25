from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    llm_model: str = "openai/gpt-oss-20b"
    lc_temperature: float = 0
    embed_model: str = "all-MiniLM-L6-v2"
    app_env: str = "development"
    max_file_size: int = 5 * 1024 * 1024
    vector_store_dir: str = "vector_store"
    log_level: str = "INFO"
    audit_db_path: str = "artifacts/audit.db"
    home_api_key: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings():
    return Settings()