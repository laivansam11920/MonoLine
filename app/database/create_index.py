from .connect_db import db

db.time_collection.create_index("username", unique=True)