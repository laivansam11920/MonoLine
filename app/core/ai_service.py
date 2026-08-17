# 1. Standard Library
from abc import ABC, abstractmethod
from typing import Any

# 2. Third-party
from google import genai
from groq import Groq

# 3. Local/Internal
from configs import Config, Prompt

__all__ = ["ai"]


class AIServices(ABC):
    def __init__(self, client: Any, model: str, prompt: str = Prompt.system_basic) -> None:
        self.client: Any = client
        self.model: str = model
        self.prompt: str = prompt
        self.error_return: str = Config.RES_DEFAULT

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

    def get_response(self) -> str:
        try:
            interaction = self.client.interactions.create(
                model=self.model, input=self.prompt
            )
            return interaction.output_text
        except Exception as e:
            print(e, flush=True)
            return self.error_return


class GroqAIServices(AIServices):
    def __init__(self) -> None:
        super().__init__(
            client=Groq(api_key=Config.GROQ_API_KEY), model=Config.MODEL_GROQ_AI
        )
        self.role: str = Config.ROLE_AI

    def __repr__(self) -> str:
        return f"<GroqAIService(model={self.model})>"

    def get_response(self) -> str:

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": self.role, "content": self.prompt}],
            temperature=0.7,
        )
        return completion.choices[0].message.content

try:
    ai = GroqAIServices()
except Exception as e:
    print(e, flush=True)
    ai = GenAIService()
