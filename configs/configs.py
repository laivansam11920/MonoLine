from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from prompts.system_prompts import sys


class Settings(BaseSettings):
    # SERVER CONFIGS
    HOST: str = Field(default="0.0.0.0", alias="HOST")
    PORT: int = Field(default=2011, alias="PORT")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    TESTING: bool = Field(default=False, alias="TESTING")

    # AI CONFIGS
    ROLE_AI: str = Field(default="user", alias="ROLE_AI")
    GROQ_API_KEY: str = Field(..., alias="GROQ_API_KEY")
    GENAI_API_KEY: str = Field(..., alias="GENAI_API_KEY")
    MODEL_GEN_AI: str = Field(
        default="gemma-4-31b-it", alias="MODEL_GEN_AI"
    )  # model_suggestion: gemini-3.1-flash-lite
    MODEL_GROQ_AI: str = Field(default="llama-3.3-70b-versatile", alias="MODEL_GROQ_AI")

    # GITHUB CONFIGS
    GITHUB_USERNAME: str = Field(..., alias="GITHUB_USERNAME")
    GITHUB_USER_TOKEN: str = Field(..., alias="GITHUB_USER_TOKEN")

    # PYDANTIC CONFIGS
    model_config = SettingsConfigDict(populate_by_name=True)

    # DATABASE CONFIGS
    DB_NAME: str = Field(default="MonoLine", alias="DB_NAME")
    URI: str = Field(..., alias="MONGO_URI")

    # TIME CONFIGS
    TIME_LIMIT: int = Field(default=3600, alias="TIME_LIMIT")


class Prompt:
    system_basic: str = sys


Config = Settings()  # type: ignore
Prompt = Prompt()

__all__ = ["Config", "Prompt"]
