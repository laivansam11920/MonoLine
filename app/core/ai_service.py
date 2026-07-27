from google import genai
from configs import Config, Prompt


class GenAIService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=Config.GENAI_API_KEY)

    def get_response(self) -> str:
        try:
            interaction = self.client.interactions.create(
                model=Config.MODEL_AI, input=Prompt.system_basic
            )
            return interaction.output_text
        except Exception as e:
            print(e, flush=True)
            return "i'm sorry"

response_text = GenAIService().get_response()

__all__ = ["response_text"]