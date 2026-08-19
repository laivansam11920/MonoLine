from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

__all__ = ["Config"]


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
    MODEL_GEN_AI: str = Field(default="gemma-4-31b-it", alias="MODEL_GEN_AI")
    MODEL_GROQ_AI: str = Field(default="openai/gpt-oss-20b", alias="MODEL_GROQ_AI")
    TOKEN_MAX_GROQ_AI: int = Field(default=100, alias="TOKEN_MAX_GROQ_AI")
    TOKEN_MAX_GEN_AI: int = Field(default=200, alias="TOKEN_MAX_GEN_AI")
    RES_DEFAULT: str = Field(default="i'm sorry", alias="RES_DEFAULT")
    TEMPERATURE: float | int = Field(default=0.7, alias="TEMPERATURE")
    MAX_CHAR: int = Field(default=10, alias="MAX_CHAR")

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
    RATELIMITE_LIMIT: int = Field(default=500, alias="RATELIMITE_LIMIT")
    RATELIMIT_PERIOD: str = Field(default="5h", alias="RATELIMIT_PERIOD")


Config = Settings()  # type: ignore