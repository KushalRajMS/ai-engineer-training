import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_env_value(key: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(key, default)
    return value


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

APP_CONFIG = {
    "provider": get_env_value("LLM_PROVIDER", "mock"),
    "model": get_env_value("LLM_MODEL", "mock-model"),
    "max_history": int(get_env_value("MAX_HISTORY_MESSAGES", "10")),
    "data_dir": str(DATA_DIR),
    "artifacts_dir": str(ARTIFACTS_DIR),
    "api_key": get_env_value("GROQ_API_KEY"),
    "temperature": float(get_env_value("LC_TEMPERATURE", "0")),
    "embed_model": get_env_value("EMBED_MODEL", "all-MiniLM-L6-v2")
}