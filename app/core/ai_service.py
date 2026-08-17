# 1. Standard Library
from abc import ABC, abstractmethod
from typing import Any

# 2. Third-party
from google import genai
from google.genai import types
from groq import Groq

# 3. Local/Internal
from configs import Config, Prompt
from app.utils.fomat_clean_text import clean_reasoning

__all__ = ["ai"]


class AIServices(ABC):
    def __init__(self, client: Any, model: str, prompt: str = Prompt.system_basic) -> None:
        self.client: Any = client
        self.model: str = model
        self.prompt: str = prompt

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def get_response(self) -> str:
        pass


class GenAIService(AIServices):
    def __init__(self) -> None:
        super().__init__(
            client=genai.Client(api_key=Config.GENAI_API_KEY), model=Config.MODEL_GEN_AI
        )

    def __repr__(self) -> str:
        return f"<GenAIService(model={self.model})>"

    @staticmethod
    def _config_ai() -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=Config.TEMPERATURE,
        )

    def get_response(self) -> str:

        interaction = self.client.models.generate_content(
            model=self.model,
            contents=self.prompt,
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

    def __repr__(self) -> str:
        return f"<GroqAIService(model={self.model})>"

    def get_response(self) -> str:

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": "Nói gì đó đi"}
            ],
            temperature=Config.TEMPERATURE,
        )
        return completion.choices[0].message.content

try:
    ai = GroqAIServices()
except Exception as e:
    print(e, flush=True)
    ai = GenAIService()

