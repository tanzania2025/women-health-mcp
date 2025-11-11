"""
Authentication module for DoctHER application.

Provides user registration, login, and session management functionality.
"""

import re
from typing import Optional, Tuple
import bcrypt
import streamlit as st
from sqlalchemy.orm import Session

from database import crud
from database.models import User


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class Authenticator:
    """
    Handles user authentication for the DoctHER application.

    Provides methods for:
    - User registration (signup)
    - User login with password verification
    - Session management
    - Password hashing and validation
    """

    def __init__(self, db_session: Session):
        """
        Initialize authenticator with database session.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password as string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to check against

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if email format is valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Requirements:
        - At least 8 characters long
        - Contains at least one letter
        - Contains at least one number

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isalpha() for c in password):
            return False, "Password must contain at least one letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        return True, ""

    def register_user(
        self, email: str, password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user account.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            Tuple of (success, message, user)
        """
        # Validate email format
        if not self.validate_email(email):
            return False, "Invalid email format", None

        # Validate password strength
        is_valid, error_msg = self.validate_password(password)
        if not is_valid:
            return False, error_msg, None

        # Check if email already exists
        existing_user = crud.get_user_by_email(self.db, email)
        if existing_user:
            return False, "Email already registered", None

        # Hash password and create user
        try:
            password_hash = self.hash_password(password)
            user = crud.create_user(
                self.db, email=email, password_hash=password_hash
            )
            return True, "Account created successfully!", user
        except Exception as e:
            return False, f"Error creating account: {str(e)}", None

    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate a user login attempt.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            Tuple of (success, message, user)
        """
        # Validate email format
        if not self.validate_email(email):
            return False, "Invalid email format", None

        # Get user by email
        user = crud.get_user_by_email(self.db, email)
        if not user:
            return False, "Invalid email or password", None

        # Check if account is active
        if not user.is_active:
            return False, "Account is deactivated", None

        # Verify password
        if not self.verify_password(password, user.password_hash):
            return False, "Invalid email or password", None

        # Update last login timestamp
        crud.update_user_last_login(self.db, user.id)

        return True, "Login successful!", user

    @staticmethod
    def init_session_state():
        """Initialize Streamlit session state for authentication."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'email' not in st.session_state:
            st.session_state.email = None

    @staticmethod
    def set_user_session(user: User):
        """
        Set user session state after successful login.

        Args:
            user: Authenticated user object
        """
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.user_id = user.id
        st.session_state.username = user.username
        st.session_state.email = user.email

    @staticmethod
    def clear_session():
        """Clear user session state (logout)."""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.email = None

        # Also clear chat-related session state
        if 'messages' in st.session_state:
            st.session_state.messages = []
        if 'current_session_id' in st.session_state:
            st.session_state.current_session_id = None

    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if user is currently authenticated.

        Returns:
            True if user is authenticated, False otherwise
        """
        return st.session_state.get('authenticated', False)

    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """
        Get the current authenticated user's ID.

        Returns:
            User ID if authenticated, None otherwise
        """
        return st.session_state.get('user_id')

    @staticmethod
    def require_authentication():
        """
        Decorator/helper to require authentication.
        Stops execution and shows login page if not authenticated.
        """
        if not Authenticator.is_authenticated():
            st.warning("Please log in to access this feature.")
            st.stop()
