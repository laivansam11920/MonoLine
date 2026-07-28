from google import genai
from configs import Config, Prompt

#

class GenAIService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=Config.GENAI_API_KEY)
        self.model = Config.MODEL_AI

    def __str__(self) -> str:
        return f"GenAIService(model='{Config.MODEL_AI}')"

    @property
    def get_response(self) -> str:
        try:
            interaction = self.client.interactions.create(
                model=self.model, input=Prompt.system_basic
            )
            return interaction.output_text
        except Exception as e:
            print(e, flush=True)
            return "i'm sorry"


ai = GenAIService()

__all__ = ["ai"]
