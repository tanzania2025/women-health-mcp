"""
Sidebar component for DoctHER application.

Provides navigation for chat history, symptom tracking, and settings.
"""

from datetime import datetime, timedelta
from typing import List, Dict
import streamlit as st
from sqlalchemy.orm import Session

from database import crud
from database.models import ChatSession
from auth import Authenticator


def group_chats_by_date(chat_sessions: List[ChatSession]) -> Dict[str, List[ChatSession]]:
    """
    Group chat sessions by date categories.

    Args:
        chat_sessions: List of chat sessions to group

    Returns:
        Dictionary with date categories as keys and lists of sessions as values
    """
    now = datetime.now()
    today = now.date()
    yesterday = (now - timedelta(days=1)).date()
    week_ago = (now - timedelta(days=7)).date()

    groups = {
        "Today": [],
        "Yesterday": [],
        "Previous 7 Days": [],
        "Older": []
    }

    for session in chat_sessions:
        session_date = session.updated_at.date()

        if session_date == today:
            groups["Today"].append(session)
        elif session_date == yesterday:
            groups["Yesterday"].append(session)
        elif session_date >= week_ago:
            groups["Previous 7 Days"].append(session)
        else:
            groups["Older"].append(session)

    return groups


def truncate_title(title: str, max_length: int = 30) -> str:
    """
    Truncate title to max length with ellipsis.

    Args:
        title: Title to truncate
        max_length: Maximum length

    Returns:
        Truncated title
    """
    if len(title) <= max_length:
        return title
    return title[:max_length - 3] + "..."


@st.dialog("Previous Chats", width="large")
def show_chat_selection_window(db_session: Session):
    """
    Display a modal window with chat history for selection.

    Args:
        db_session: SQLAlchemy database session
    """
    # Add custom CSS for the dialog buttons and width
    st.markdown("""
        <style>
        /* Make dialog wider to fit chat titles on one line */
        div[data-testid="stDialog"] {
            max-width: 800px !important;
            width: 90vw !important;
        }

        div[data-testid="stDialog"] > div {
            max-width: 800px !important;
        }

        /* Override button styling in dialog - rectangular buttons spanning full width */
        div[data-testid="stDialog"] .stButton > button {
            border-radius: 4px !important;
            padding: 12px 16px !important;
            width: 100% !important;
            height: auto !important;
            min-height: auto !important;
            max-height: none !important;
            text-align: left !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            font-size: 15px !important;
            display: block !important;
        }
        </style>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("Please log in to view chat history")
        return

    # Get user's chat sessions
    chat_sessions = crud.get_user_chat_sessions(db_session, user_id, limit=50)

    if not chat_sessions:
        st.info("No previous chats found. Start a new conversation!")
        return

    # Group by date
    grouped_chats = group_chats_by_date(chat_sessions)

    # Display grouped chats
    for category, sessions in grouped_chats.items():
        if sessions:  # Only show category if it has chats
            st.markdown(f"### {category}")

            for session in sessions:
                # Get full title
                display_title = session.title or "Untitled Chat"

                # Check if this is the current session
                is_current = (
                    st.session_state.get('current_session_id') == session.id
                )

                # Show title as button with indicator prefix if current - full width rectangular button
                button_text = f"▶ {display_title}" if is_current else display_title
                if st.button(
                    button_text,
                    key=f"chat_{session.id}",
                    disabled=is_current,
                    use_container_width=True,
                    type="secondary"
                ):
                    # Load this chat session
                    load_chat_session(db_session, session.id)
                    st.session_state.show_chat_window = False
                    st.rerun()

            st.markdown("---")


def show_sidebar(db_session: Session):
    """
    Display the application sidebar with navigation and chat history.

    Args:
        db_session: SQLAlchemy database session
    """
    with st.sidebar:
        # Icon-only navigation with clean minimal icons
        # Temporary placeholders until Phosphor icons are properly implemented

        # New Chat button
        if st.button("➕", use_container_width=True, help="New Chat", key="new_chat_btn"):
            # Clear current session and start fresh
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.session_state.tool_logs = []
            st.session_state.show_chat_window = False
            st.session_state.show_symptom_form = False
            st.session_state.show_symptom_tracker = False
            st.session_state.is_processing = False
            st.session_state.pending_message = ""
            st.session_state.pending_input = ""
            st.session_state.symptom_extraction_cache = None
            st.session_state.symptom_text_to_record = None
            st.session_state.current_input_text = ""
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Previous Chats button
        if st.button("💬", use_container_width=True, help="Previous Chats", key="previous_chats_btn"):
            st.session_state.show_chat_window = True
            st.rerun()

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Symptom Tracker Button
        if st.button("📊", use_container_width=True, help="Symptom Tracker", key="symptom_tracker_btn"):
            st.session_state.show_symptom_tracker = True
            st.session_state.show_chat_window = False
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Logout Button
        authenticator = Authenticator(db_session)
        if st.button("🚪", use_container_width=True, help="Logout", key="logout_btn"):
            authenticator.clear_session()
            st.rerun()


def load_chat_session(db_session: Session, session_id: int):
    """
    Load a chat session's messages into the current state.

    Args:
        db_session: SQLAlchemy database session
        session_id: ID of the chat session to load
    """
    # Get session and messages
    session = crud.get_chat_session(db_session, session_id)
    if not session:
        st.error("Chat session not found")
        return

    messages = crud.get_session_messages(db_session, session_id)

    # Load into session state
    st.session_state.current_session_id = session_id
    st.session_state.messages = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    # Load tool logs for each message
    st.session_state.tool_logs = []
    for msg in messages:
        tool_logs = crud.get_message_tool_logs(db_session, msg.id)
        for log in tool_logs:
            st.session_state.tool_logs.append({
                "tool": log.tool_name,
                "input": log.tool_input,
                "output": log.tool_output,
            })

    # Clear symptom tracker view if active
    if 'show_symptom_tracker' in st.session_state:
        st.session_state.show_symptom_tracker = False

    st.rerun()


def init_chat_session(db_session: Session):
    """
    Initialize a chat session for the current user if none exists.

    Note: Does not auto-load or auto-create sessions.
    - Users start on the landing page
    - Sessions are created when user sends first message
    - Previous sessions are loaded manually via the "Previous Chats" button

    Args:
        db_session: SQLAlchemy database session
    """
    # No auto-loading - users manually select previous chats or start new ones
    pass
