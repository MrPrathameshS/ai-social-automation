print(">>> Script started")

from app.db.base import Base
from app.db.session import engine
from app.db import models

print(">>> Imports successful, creating tables...")

Base.metadata.create_all(bind=engine)

print(">>> Tables created successfully")
