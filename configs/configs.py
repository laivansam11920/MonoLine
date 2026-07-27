from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(find_dotenv(), override=True)

BASE_DIR = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = BASE_DIR / "system.prompt"


class Settings(BaseSettings):
    # SERVER CONFIGS
    HOST: str = Field(default="0.0.0.0", alias="HOST")
    PORT: int = Field(default=2011, alias="PORT")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    TESTING: bool = Field(default=False, alias="TESTING")

    # AI CONFIGS
    GENAI_API_KEY: str = Field(..., alias="GENAI_API_KEY")
    MODEL_AI: str = Field(
        default="gemma-4-31b-it", alias="MODEL_AI"
    )  # model_suggestion: gemini-3.1-flash-lite

    # GITHUB CONFIGS
    GITHUB_USERNAME: str = Field(..., alias="GITHUB_USERNAME")
    GITHUB_USER_TOKEN: str = Field(..., alias="GITHUB_USER_TOKEN")

    # PYDANTIC CONFIGS
    model_config = SettingsConfigDict(populate_by_name=True)

    # DATABASE CONFIGS
    DB_NAME: str = Field(default="MonoLine", alias="DB_NAME")
    URI: str = Field(..., alias="MONGO_URI")


class Prompt:
    system_basic: str = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


Config = Settings()  # type: ignore
Prompt = Prompt()

__all__ = ["Config", "Prompt"]
