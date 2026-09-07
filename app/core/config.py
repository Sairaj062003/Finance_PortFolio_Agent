from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project (root directory)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    DEFAULT_MODEL: str = "gemini-3.6-flash"
    PORTFOLIO_DATA_PATH: Path = BASE_DIR / "data" / "portfolio.json"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
