from dotenv import load_dotenv, find_dotenv

__all__ = ["Config", "Prompt"]

load_dotenv(find_dotenv(), override=True)

from .configs import *
