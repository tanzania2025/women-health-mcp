"""
Database models for DoctHER application.

Includes models for:
- User authentication and management
- Chat sessions and message history
- Tool usage logs
- Symptom tracking and analysis
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """User account model for authentication and data ownership."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)  # Optional, derived from email
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)  # Admin access for analytics dashboard

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class ChatSession(Base):
    """Chat session model for organizing conversation history."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.timestamp")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(Base):
    """Message model for storing individual chat messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    tool_logs = relationship("ToolLog", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"


class ToolLog(Base):
    """Tool usage log model for tracking MCP tool calls."""

    __tablename__ = "tool_logs"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(Text, nullable=True)
    tool_output = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    message = relationship("Message", back_populates="tool_logs")

    def __repr__(self):
        return f"<ToolLog(id={self.id}, tool_name={self.tool_name}, message_id={self.message_id})>"


class Symptom(Base):
    """Symptom tracking model for health monitoring."""

    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Core fields (required)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    symptom_type = Column(String(100), nullable=False, index=True)  # e.g., 'pain', 'bleeding', 'mood'
    body_part = Column(String(100), nullable=True)  # e.g., 'abdomen', 'lower back', 'head'
    duration = Column(String(100), nullable=True)  # e.g., '2 hours', '3 days', 'ongoing'
    symptom_time = Column(DateTime, nullable=False, index=True)  # When symptom occurred - indexed for date queries

    # Extended fields
    severity = Column(Integer, nullable=True)  # 1-10 scale
    description = Column(Text, nullable=True)  # Free text description from user
    related_symptoms = Column(Text, nullable=True)  # Comma-separated or JSON list
    triggers = Column(Text, nullable=True)  # Possible triggers identified
    notes = Column(Text, nullable=True)  # Additional notes

    # Cycle tracking (optional)
    cycle_day = Column(Integer, nullable=True)  # Day of menstrual cycle if applicable

    # Metadata
    raw_input = Column(Text, nullable=True)  # Original user input before extraction
    extraction_data = Column(Text, nullable=True)  # Full LLM extraction as JSON

    # Relationships
    user = relationship("User", back_populates="symptoms")

    def __repr__(self):
        return f"<Symptom(id={self.id}, user_id={self.user_id}, type={self.symptom_type}, time={self.symptom_time})>"


class UserActivity(Base):
    """Track user login and activity patterns."""

    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'login', 'logout', 'page_view', 'session_start', 'session_end'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)  # Browser session ID
    page = Column(String(100), nullable=True)  # Page/view name (e.g., 'chat', 'symptom_tracker', 'symptom_form')
    meta_data = Column(Text, nullable=True)  # JSON for additional data

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserActivity(user_id={self.user_id}, event={self.event_type}, time={self.timestamp})>"


class APIUsage(Base):
    """Track Anthropic API usage for cost monitoring and analytics."""

    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # API details
    model = Column(String(100), nullable=False)  # e.g., 'claude-sonnet-4-20250514'
    operation = Column(String(100), nullable=False)  # e.g., 'chat', 'symptom_extraction'

    # Token usage
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)

    # Cost estimation (in USD)
    estimated_cost = Column(Float, nullable=True)

    # Request/response details
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<APIUsage(model={self.model}, tokens={self.total_tokens}, cost=${self.estimated_cost})>"


class FeatureUsage(Base):
    """Track usage of specific application features."""

    __tablename__ = "feature_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(100), nullable=False, index=True)  # e.g., 'symptom_record', 'chat_message', 'symptom_tracker_view'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    count = Column(Integer, default=1, nullable=False)  # Number of times used in this event
    meta_data = Column(Text, nullable=True)  # JSON for additional context

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<FeatureUsage(user_id={self.user_id}, feature={self.feature_name}, time={self.timestamp})>"


class SystemMetric(Base):
    """Track system performance and health metrics."""

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metric_type = Column(String(100), nullable=False, index=True)  # e.g., 'db_query', 'page_load', 'error'
    metric_value = Column(Float, nullable=False)  # e.g., query time in ms, load time in seconds
    context = Column(String(200), nullable=True)  # e.g., 'get_user_symptoms', 'symptom_dashboard'
    meta_data = Column(Text, nullable=True)  # JSON for additional data

    def __repr__(self):
        return f"<SystemMetric(type={self.metric_type}, value={self.metric_value}, time={self.timestamp})>"


# Database session management
def get_engine(database_url: str = "sqlite:///./womens_health_mcp.db"):
    """
    Create and return database engine with appropriate configuration.

    For PostgreSQL (production): Uses connection pooling for better performance
    For SQLite (development): Uses check_same_thread=False for Streamlit compatibility

    Args:
        database_url: Database connection URL

    Returns:
        SQLAlchemy engine instance
    """
    if database_url.startswith("postgresql"):
        # Production PostgreSQL configuration optimized for Streamlit Cloud
        return create_engine(
            database_url,
            pool_size=2,  # Reduced for Streamlit Cloud's architecture
            max_overflow=3,  # Smaller overflow for faster connection reuse
            pool_pre_ping=True,  # Verify connections are alive before using
            pool_recycle=300,  # Recycle connections every 5 minutes (faster refresh)
            connect_args={
                "connect_timeout": 10,  # 10 second connection timeout
                "options": "-c statement_timeout=30000"  # 30 second query timeout
            },
            echo=False,
        )
    else:
        # Development SQLite configuration
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False,  # Set to True for SQL debugging
        )


def get_session_maker(engine):
    """Create and return session maker."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(database_url: str = "sqlite:///./womens_health_mcp.db"):
    """Initialize database tables."""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
