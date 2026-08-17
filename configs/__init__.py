from dotenv import load_dotenv, find_dotenv
from app.utils.logger import logger

__all__ = ["Config"]

if not load_dotenv(find_dotenv(), override=True):
    logger.critical("NO .ENV FILE FOUND")

from .configs import *