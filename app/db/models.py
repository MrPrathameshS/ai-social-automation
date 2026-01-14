from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

from app.db.base import Base


# =========================
# CLIENT (Tenant)
# =========================
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="client", cascade="all, delete-orphan")
    brand = relationship("BrandProfile", back_populates="client", uselist=False, cascade="all, delete-orphan")


# =========================
# USER
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="users")


# =========================
# BRAND (1:1 with Client)
# =========================
class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    platform = Column(String(50), nullable=False)  # linkedin, instagram, facebook
    page_id = Column(String(255), nullable=True)

    tone_description = Column(Text, nullable=True)
    audience_description = Column(Text, nullable=True)
    writing_style = Column(Text, nullable=True)
    do_not_use = Column(Text, nullable=True)
    learned_insights = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    approval_required = Column(Boolean, default=True)
    voice_version = Column(String(50), default="v1")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# =========================
# TOPIC (per brand)
# =========================
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    topic_text = Column(Text, nullable=False)

    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    brand = relationship("BrandProfile", back_populates="topics")

    created_at = Column(DateTime, default=datetime.utcnow)

    contents = relationship("ContentItem", back_populates="topic", cascade="all, delete-orphan")


# =========================
# CONTENT ITEM (Pipeline object)
# =========================
class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    platform = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    generated_text = Column(Text)
    asset_path = Column(String)
    status = Column(String, default="PENDING_APPROVAL")
    error_message = Column(Text, nullable=True)

    topic = relationship("Topic", back_populates="contents")
    schedules = relationship("Schedule", back_populates="content", cascade="all, delete-orphan")


# =========================
# GENERATED CONTENT (Legacy / External)
# =========================
class GeneratedContent(Base):
    __tablename__ = "generated_contents"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    platform = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    content_text = Column(Text)

    status = Column(String, default="pending")
    scheduled_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)

    prompt_version = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("BrandProfile")
    topic = relationship("Topic")



# =========================
# APPROVAL BATCH
# =========================
class ApprovalBatch(Base):
    __tablename__ = "approval_batches"

    id = Column(Integer, primary_key=True, index=True)
    filter_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# SCHEDULE
# =========================
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)

    content = relationship("ContentItem", back_populates="schedules")


# =========================
# LOG
# =========================
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, nullable=True)
    step = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


# =========================
# POSTING STRATEGY
# =========================
class PostingStrategy(Base):
    __tablename__ = "posting_strategies"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    strategy_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# PROMPT TEMPLATE
# =========================
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    platform = Column(String, nullable=False)
    version = Column(Integer, default=1)
    prompt_text = Column(Text, nullable=False)
    mutation_reason = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("BrandProfile", back_populates="prompts")


# =========================
# ENGAGEMENT LOG
# =========================
class EngagementLog(Base):
    __tablename__ = "engagement_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("generated_contents.id"), nullable=False)

    platform = Column(String, nullable=False)

    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


# =========================
# BRAND MUTATION LOG
# =========================
class BrandMutationLog(Base):
    __tablename__ = "brand_mutation_logs"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)

    field_mutated = Column(String)
    old_value = Column(Text)
    new_value = Column(Text)

    mutation_reason = Column(Text)
    performance_snapshot = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# PROMPT PERFORMANCE LOG
# =========================
class PromptPerformanceLog(Base):
    __tablename__ = "prompt_performance_logs"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    prompt_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False)

    platform = Column(String, nullable=False)

    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)

    engagement_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
