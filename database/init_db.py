#!/usr/bin/env python
"""
Database initialization script for DoctHER application.

Usage:
    python -m database.init_db
"""

import os
from pathlib import Path
from .models import init_db, get_engine, Base

def initialize_database(database_url: str = None):
    """
    Initialize the database with all tables.

    Args:
        database_url: Database URL. Defaults to SQLite in project root.
    """
    if database_url is None:
        # Default to SQLite in project root
        project_root = Path(__file__).parent.parent
        db_path = project_root / "womens_health_mcp.db"
        database_url = f"sqlite:///{db_path}"

    print(f"Initializing database at: {database_url}")

    # Create engine and tables
    engine = init_db(database_url)

    print("Database tables created successfully:")
    print("  - users")
    print("  - chat_sessions")
    print("  - messages")
    print("  - tool_logs")
    print("  - symptoms")
    print("\nDatabase initialization complete!")

    return engine


if __name__ == "__main__":
    initialize_database()
