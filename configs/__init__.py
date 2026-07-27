from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

from .configs import *

__all__ = ["Config", 'Prompt']