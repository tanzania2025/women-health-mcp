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

# ==================== Analytics Operations ====================

def get_user_activity_stats(db: Session, days: int = 30) -> dict:
    """Get user activity statistics for the past N days."""
    from datetime import timedelta
    from .models import UserActivity
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total unique users
    total_users = db.query(User).count()
    
    # Active users (logged in during period)
    active_users = db.query(func.count(func.distinct(UserActivity.user_id))).filter(
        UserActivity.timestamp >= start_date,
        UserActivity.event_type == 'login'
    ).scalar() or 0
    
    # Total logins
    total_logins = db.query(UserActivity).filter(
        UserActivity.timestamp >= start_date,
        UserActivity.event_type == 'login'
    ).count()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_logins': total_logins,
        'period_days': days
    }


def get_feature_usage_stats(db: Session, days: int = 30) -> dict:
    """Get feature usage statistics."""
    from datetime import timedelta
    from .models import FeatureUsage
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total symptoms recorded
    symptoms_recorded = db.query(func.sum(FeatureUsage.count)).filter(
        FeatureUsage.timestamp >= start_date,
        FeatureUsage.feature_name == 'symptom_record'
    ).scalar() or 0
    
    # Total chat messages
    chat_messages = db.query(func.sum(FeatureUsage.count)).filter(
        FeatureUsage.timestamp >= start_date,
        FeatureUsage.feature_name == 'chat_message'
    ).scalar() or 0
    
    # Symptom tracker views
    tracker_views = db.query(func.sum(FeatureUsage.count)).filter(
        FeatureUsage.timestamp >= start_date,
        FeatureUsage.feature_name == 'symptom_tracker_view'
    ).scalar() or 0
    
    # Most used symptom types
    top_symptoms = db.query(Symptom.symptom_type, func.count(Symptom.id).label('count')).filter(
        Symptom.recorded_at >= start_date
    ).group_by(Symptom.symptom_type).order_by(desc('count')).limit(5).all()
    
    return {
        'symptoms_recorded': int(symptoms_recorded),
        'chat_messages': int(chat_messages),
        'tracker_views': int(tracker_views),
        'top_symptom_types': [(s[0], s[1]) for s in top_symptoms],
        'period_days': days
    }


def get_api_usage_stats(db: Session, days: int = 30) -> dict:
    """Get API usage and cost statistics."""
    from datetime import timedelta
    from .models import APIUsage
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total API calls
    total_calls = db.query(APIUsage).filter(
        APIUsage.timestamp >= start_date
    ).count()
    
    # Successful calls
    successful_calls = db.query(APIUsage).filter(
        APIUsage.timestamp >= start_date,
        APIUsage.success == True
    ).count()
    
    # Total tokens
    total_input_tokens = db.query(func.sum(APIUsage.input_tokens)).filter(
        APIUsage.timestamp >= start_date
    ).scalar() or 0
    
    total_output_tokens = db.query(func.sum(APIUsage.output_tokens)).filter(
        APIUsage.timestamp >= start_date
    ).scalar() or 0
    
    # Total cost
    total_cost = db.query(func.sum(APIUsage.estimated_cost)).filter(
        APIUsage.timestamp >= start_date
    ).scalar() or 0.0
    
    # Average response time
    avg_response_time = db.query(func.avg(APIUsage.response_time_ms)).filter(
        APIUsage.timestamp >= start_date,
        APIUsage.response_time_ms.isnot(None)
    ).scalar() or 0
    
    # Breakdown by operation
    operations = db.query(
        APIUsage.operation,
        func.count(APIUsage.id).label('count'),
        func.sum(APIUsage.total_tokens).label('tokens'),
        func.sum(APIUsage.estimated_cost).label('cost')
    ).filter(
        APIUsage.timestamp >= start_date
    ).group_by(APIUsage.operation).all()
    
    return {
        'total_calls': total_calls,
        'successful_calls': successful_calls,
        'failed_calls': total_calls - successful_calls,
        'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
        'total_input_tokens': int(total_input_tokens),
        'total_output_tokens': int(total_output_tokens),
        'total_tokens': int(total_input_tokens + total_output_tokens),
        'total_cost': round(total_cost, 4),
        'avg_response_time_ms': round(avg_response_time, 2) if avg_response_time else 0,
        'operations': [(op[0], op[1], int(op[2] or 0), round(op[3] or 0, 4)) for op in operations],
        'period_days': days
    }


def get_system_metrics_stats(db: Session, days: int = 30) -> dict:
    """Get system performance metrics."""
    from datetime import timedelta
    from .models import SystemMetric
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Average DB query time
    avg_db_query = db.query(func.avg(SystemMetric.metric_value)).filter(
        SystemMetric.timestamp >= start_date,
        SystemMetric.metric_type == 'db_query'
    ).scalar() or 0
    
    # Average page load time
    avg_page_load = db.query(func.avg(SystemMetric.metric_value)).filter(
        SystemMetric.timestamp >= start_date,
        SystemMetric.metric_type == 'page_load'
    ).scalar() or 0
    
    # Error count
    error_count = db.query(SystemMetric).filter(
        SystemMetric.timestamp >= start_date,
        SystemMetric.metric_type == 'error'
    ).count()
    
    return {
        'avg_db_query_ms': round(avg_db_query, 2) if avg_db_query else 0,
        'avg_page_load_s': round(avg_page_load, 2) if avg_page_load else 0,
        'error_count': error_count,
        'period_days': days
    }


def get_user_last_page(db: Session, user_id: int) -> Optional[str]:
    """Get the last page a user visited."""
    from .models import UserActivity
    
    activity = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.event_type == 'page_view',
        UserActivity.page.isnot(None)
    ).order_by(desc(UserActivity.timestamp)).first()
    
    return activity.page if activity else None


def get_all_users_activity(db: Session, limit: int = 100) -> List[dict]:
    """Get recent activity for all users."""
    from .models import UserActivity
    
    users = db.query(User).order_by(desc(User.last_login)).limit(limit).all()
    
    result = []
    for user in users:
        # Get last page
        last_page = get_user_last_page(db, user.id)
        
        # Get last activity
        last_activity = db.query(UserActivity).filter(
            UserActivity.user_id == user.id
        ).order_by(desc(UserActivity.timestamp)).first()
        
        # Count symptoms
        symptom_count = db.query(Symptom).filter(Symptom.user_id == user.id).count()
        
        # Count chat sessions
        chat_count = db.query(ChatSession).filter(ChatSession.user_id == user.id).count()
        
        result.append({
            'user_id': user.id,
            'email': user.email,
            'created_at': user.created_at,
            'last_login': user.last_login,
            'last_page': last_page,
            'last_activity': last_activity.timestamp if last_activity else None,
            'symptom_count': symptom_count,
            'chat_count': chat_count,
            'is_admin': user.is_admin
        })
    
    return result
