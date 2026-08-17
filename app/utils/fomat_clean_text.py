import re

def clean_reasoning(text: str) -> str:
    if not text:
        return ""

    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()
