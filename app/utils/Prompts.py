from pathlib import Path
from app.utils.logger import logger

BASE_DIR = Path(__file__).resolve().parents[2]

target_file = BASE_DIR / "default_prompt.monoline"

try:
    SYSTEM_PROMPT = target_file.read_text(encoding="utf-8")
except Exception as e:
    logger.error(e)