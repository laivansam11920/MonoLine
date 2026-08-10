# 1. Local/Internal
from .connect_db import db

db.time_limit.create_index("username", unique=True)
