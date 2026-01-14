from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 🔥 CRITICAL: import all models so SQLAlchemy registers them
from app.db.models import *
