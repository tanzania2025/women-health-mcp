"""Authentication package for DoctHER application."""

from .authenticator import Authenticator, AuthenticationError

__all__ = ["Authenticator", "AuthenticationError"]
