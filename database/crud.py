"""
CRUD operations for DoctHER database.

Provides functions for Create, Read, Update, Delete operations
for all database models.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .models import User, ChatSession, Message, ToolLog, Symptom


# ==================== User Operations ====================

def create_user(db: Session, email: str, password_hash: str, username: str = None) -> User:
    """Create a new user account."""
    # Generate username from email if not provided
    if not username:
        username = email.split('@')[0]

    user = User(
        email=email,
        username=username,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def update_user_last_login(db: Session, user_id: int) -> None:
    """Update user's last login timestamp."""
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


# ==================== Chat Session Operations ====================

def create_chat_session(db: Session, user_id: int, title: Optional[str] = None) -> ChatSession:
    """Create a new chat session for a user."""
    session = ChatSession(
        user_id=user_id,
        title=title or "New Chat",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
    """Get a chat session by ID."""
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()


def get_user_chat_sessions(
    db: Session, user_id: int, limit: int = 50, offset: int = 0
) -> List[ChatSession]:
    """Get all chat sessions for a user, ordered by most recent."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(desc(ChatSession.updated_at))
        .limit(limit)
        .offset(offset)
        .all()
    )


def update_chat_session_title(db: Session, session_id: int, title: str) -> Optional[ChatSession]:
    """Update the title of a chat session."""
    session = get_chat_session(db, session_id)
    if session:
        session.title = title
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def delete_chat_session(db: Session, session_id: int) -> bool:
    """Delete a chat session and all associated messages."""
    session = get_chat_session(db, session_id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False


# ==================== Message Operations ====================

def create_message(
    db: Session, session_id: int, role: str, content: str
) -> Message:
    """Create a new message in a chat session."""
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
    )
    db.add(message)

    # Update session's updated_at timestamp
    session = get_chat_session(db, session_id)
    if session:
        session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)
    return message


def get_session_messages(
    db: Session, session_id: int, limit: Optional[int] = None
) -> List[Message]:
    """Get all messages for a chat session."""
    query = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp)
    if limit:
        query = query.limit(limit)
    return query.all()


def get_message_by_id(db: Session, message_id: int) -> Optional[Message]:
    """Get a message by ID."""
    return db.query(Message).filter(Message.id == message_id).first()


# ==================== Tool Log Operations ====================

def create_tool_log(
    db: Session,
    message_id: int,
    tool_name: str,
    tool_input: Optional[str] = None,
    tool_output: Optional[str] = None,
) -> ToolLog:
    """Create a tool usage log entry."""
    tool_log = ToolLog(
        message_id=message_id,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_output=tool_output,
    )
    db.add(tool_log)
    db.commit()
    db.refresh(tool_log)
    return tool_log


def get_message_tool_logs(db: Session, message_id: int) -> List[ToolLog]:
    """Get all tool logs for a message."""
    return db.query(ToolLog).filter(ToolLog.message_id == message_id).all()


# ==================== Symptom Operations ====================

def create_symptom(
    db: Session,
    user_id: int,
    symptom_type: str,
    body_part: Optional[str] = None,
    duration: Optional[str] = None,
    symptom_time: Optional[datetime] = None,
    severity: Optional[int] = None,
    description: Optional[str] = None,
    related_symptoms: Optional[str] = None,
    triggers: Optional[str] = None,
    notes: Optional[str] = None,
    cycle_day: Optional[int] = None,
    raw_input: Optional[str] = None,
    extraction_data: Optional[str] = None,
) -> Symptom:
    """Create a new symptom record."""
    symptom = Symptom(
        user_id=user_id,
        symptom_type=symptom_type,
        body_part=body_part,
        duration=duration,
        symptom_time=symptom_time or datetime.utcnow(),
        severity=severity,
        description=description,
        related_symptoms=related_symptoms,
        triggers=triggers,
        notes=notes,
        cycle_day=cycle_day,
        raw_input=raw_input,
        extraction_data=extraction_data,
    )
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom


def get_user_symptoms(
    db: Session,
    user_id: int,
    symptom_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Symptom]:
    """Get symptoms for a user with optional filters."""
    query = db.query(Symptom).filter(Symptom.user_id == user_id)

    if symptom_type:
        query = query.filter(Symptom.symptom_type == symptom_type)

    if start_date:
        query = query.filter(Symptom.symptom_time >= start_date)

    if end_date:
        query = query.filter(Symptom.symptom_time <= end_date)

    return query.order_by(desc(Symptom.symptom_time)).limit(limit).offset(offset).all()


def get_symptom_by_id(db: Session, symptom_id: int) -> Optional[Symptom]:
    """Get a symptom by ID."""
    return db.query(Symptom).filter(Symptom.id == symptom_id).first()


def get_symptom_types_for_user(db: Session, user_id: int) -> List[str]:
    """Get all unique symptom types for a user."""
    results = (
        db.query(Symptom.symptom_type)
        .filter(Symptom.user_id == user_id)
        .distinct()
        .all()
    )
    return [r[0] for r in results if r[0]]


def get_symptom_stats(db: Session, user_id: int, symptom_type: Optional[str] = None):
    """Get statistics about symptoms for a user."""
    query = db.query(Symptom).filter(Symptom.user_id == user_id)

    if symptom_type:
        query = query.filter(Symptom.symptom_type == symptom_type)

    total_count = query.count()

    if total_count == 0:
        return {
            "total_count": 0,
            "avg_severity": None,
            "most_common_location": None,
            "first_recorded": None,
            "last_recorded": None,
        }

    avg_severity = query.filter(Symptom.severity.isnot(None)).with_entities(
        func.avg(Symptom.severity)
    ).scalar()

    # Most common body part
    most_common_location = (
        query.filter(Symptom.body_part.isnot(None))
        .with_entities(Symptom.body_part, func.count(Symptom.body_part))
        .group_by(Symptom.body_part)
        .order_by(desc(func.count(Symptom.body_part)))
        .first()
    )

    first_symptom = query.order_by(Symptom.symptom_time).first()
    last_symptom = query.order_by(desc(Symptom.symptom_time)).first()

    return {
        "total_count": total_count,
        "avg_severity": round(avg_severity, 1) if avg_severity else None,
        "most_common_location": most_common_location[0] if most_common_location else None,
        "first_recorded": first_symptom.symptom_time if first_symptom else None,
        "last_recorded": last_symptom.symptom_time if last_symptom else None,
    }


def delete_symptom(db: Session, symptom_id: int) -> bool:
    """Delete a symptom record."""
    symptom = get_symptom_by_id(db, symptom_id)
    if symptom:
        db.delete(symptom)
        db.commit()
        return True
    return False


def update_null_severities_to_default(db: Session, default_severity: int = 5) -> int:
    """
    Update all symptom records with NULL severity to a default value.

    Args:
        db: Database session
        default_severity: Default severity value (1-10 scale), defaults to 5

    Returns:
        Number of records updated
    """
    # Query all symptoms with NULL severity
    symptoms_to_update = db.query(Symptom).filter(Symptom.severity.is_(None)).all()

    count = len(symptoms_to_update)

    if count > 0:
        # Update each symptom
        for symptom in symptoms_to_update:
            symptom.severity = default_severity

        # Commit all changes
        db.commit()

    return count
