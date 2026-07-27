
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

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
  REPO_README_NAME: str = Field(..., alias="REPO_README_NAME")

  # Pydantic Config
  model_config = SettingsConfigDict(populate_by_name=True)

class Prompt:
    system_basic: str = "xin chao"

Config = Settings() # type: ignore
Prompt = Prompt()