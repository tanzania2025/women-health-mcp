"""
Usage tracking utilities for DoctHER application.

Provides functions to track user activity, API usage, feature usage, and system metrics.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from database.models import UserActivity, APIUsage, FeatureUsage, SystemMetric


def track_user_activity(
    db: Session,
    user_id: int,
    event_type: str,
    page: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Track user activity event.

    Args:
        db: Database session
        user_id: User ID
        event_type: Type of event (login, logout, page_view, session_start, session_end)
        page: Current page/view name
        session_id: Browser session ID
        metadata: Additional data as dictionary
    """
    try:
        activity = UserActivity(
            user_id=user_id,
            event_type=event_type,
            page=page,
            session_id=session_id,
            meta_data=json.dumps(metadata) if metadata else None,
            timestamp=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error tracking user activity: {e}")


def track_api_usage(
    db: Session,
    model: str,
    operation: str,
    input_tokens: int,
    output_tokens: int,
    user_id: Optional[int] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    response_time_ms: Optional[int] = None
):
    """
    Track Anthropic API usage.

    Args:
        db: Database session
        model: Model name (e.g., 'claude-sonnet-4-20250514')
        operation: Operation type (e.g., 'chat', 'symptom_extraction')
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        user_id: User ID (optional)
        success: Whether the API call succeeded
        error_message: Error message if failed
        response_time_ms: Response time in milliseconds
    """
    try:
        # Calculate total tokens
        total_tokens = input_tokens + output_tokens

        # Estimate cost (Claude Sonnet 4 pricing as of 2025)
        # Input: $3 per million tokens, Output: $15 per million tokens
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        estimated_cost = input_cost + output_cost

        usage = APIUsage(
            user_id=user_id,
            model=model,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            success=success,
            error_message=error_message,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow()
        )
        db.add(usage)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error tracking API usage: {e}")


def track_feature_usage(
    db: Session,
    user_id: int,
    feature_name: str,
    count: int = 1,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Track feature usage.

    Args:
        db: Database session
        user_id: User ID
        feature_name: Feature name (e.g., 'symptom_record', 'chat_message', 'symptom_tracker_view')
        count: Number of times used
        metadata: Additional context
    """
    try:
        usage = FeatureUsage(
            user_id=user_id,
            feature_name=feature_name,
            count=count,
            meta_data=json.dumps(metadata) if metadata else None,
            timestamp=datetime.utcnow()
        )
        db.add(usage)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error tracking feature usage: {e}")


def track_system_metric(
    db: Session,
    metric_type: str,
    metric_value: float,
    context: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Track system performance metric.

    Args:
        db: Database session
        metric_type: Type of metric (e.g., 'db_query', 'page_load', 'error')
        metric_value: Metric value (e.g., time in ms, error count)
        context: Context (e.g., function name, endpoint)
        metadata: Additional data
    """
    try:
        metric = SystemMetric(
            metric_type=metric_type,
            metric_value=metric_value,
            context=context,
            meta_data=json.dumps(metadata) if metadata else None,
            timestamp=datetime.utcnow()
        )
        db.add(metric)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error tracking system metric: {e}")


def update_last_page(
    db: Session,
    user_id: int,
    page: str,
    session_id: Optional[str] = None
):
    """
    Update user's last visited page.

    Args:
        db: Database session
        user_id: User ID
        page: Page name
        session_id: Browser session ID
    """
    track_user_activity(
        db=db,
        user_id=user_id,
        event_type="page_view",
        page=page,
        session_id=session_id
    )
