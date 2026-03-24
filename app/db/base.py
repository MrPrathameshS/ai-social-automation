from sqlalchemy.orm import declarative_base

Base = declarative_base()


# import models so Alembic can detect them

from app.db.models.conversation_session import ConversationSession
from app.db.models.conversation_message import ConversationMessage
from app.db.models.conversation_state import ConversationState
from app.db.models.insight import Insight