from abc import ABC, abstractmethod
from typing import Any

from google import genai
from google.genai import types
from groq import Groq

from configs import Config
from app.utils.logger import logger
from app.utils.Prompts import SYSTEM_PROMPT

__all__ = ["ai"]


class AIServices(ABC):
    def __init__(self, client: Any, model: str, prompt: str = SYSTEM_PROMPT) -> None:
        self.client: Any = client
        self.model: str = model
        self.prompt: str = prompt

    @abstractmethod
    def get_response(self) -> str:
        pass


class GenAIService(AIServices):
    def __init__(self) -> None:
        super().__init__(
            client=genai.Client(api_key=Config.GENAI_API_KEY), model=Config.MODEL_GEN_AI
        )

    @staticmethod
    def _config_ai() -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=Config.TEMPERATURE,
        )

    def get_response(self) -> str:

        interaction = self.client.models.generate_content(
            model=self.model,
            contents=f"System:{self.prompt} ||| Character limit:{Config.MAX_CHAR}",
            config=self._config_ai(),
        )

        if not interaction or not interaction.text:
            return Config.RES_DEFAULT
        return interaction.text


class GroqAIServices(AIServices):
    def __init__(self) -> None:
        super().__init__(
            client=Groq(api_key=Config.GROQ_API_KEY), model=Config.MODEL_GROQ_AI
        )

    def get_response(self) -> str:

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": f"Character limit:{Config.MAX_CHAR}"},
            ],
            temperature=Config.TEMPERATURE,
            reasoning_effort="low",
        )

        if (
                completion
                and completion.choices
                and len(completion.choices) > 0
                and completion.choices[0].message
                and completion.choices[0].message.content
        ):
            return completion.choices[0].message.content
        return Config.RES_DEFAULT


try:
    ai = GroqAIServices()
except Exception as e:
    logger.error(e)
    ai = GenAIService()
