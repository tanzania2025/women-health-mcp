#!/usr/bin/env python3
"""
Quick migration runner to add is_admin column.

This can be run directly or imported and called from Streamlit.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import text, inspect

from database.models import init_db, get_session_maker

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./womens_health_mcp.db")


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_admin_column():
    """Add is_admin column to users table if it doesn't exist."""
    print("=" * 60)
    print("Database Migration: Add is_admin Column")
    print("=" * 60)
    print(f"Database: {DATABASE_URL[:50]}...")

    engine = init_db(DATABASE_URL)
    SessionLocal = get_session_maker(engine)
    db = SessionLocal()

    try:
        # Check if column exists
        if check_column_exists(engine, 'users', 'is_admin'):
            print("✓ is_admin column already exists")
            return True

        print("Adding is_admin column to users table...")

        if DATABASE_URL.startswith("sqlite"):
            # SQLite
            db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL"))
        elif DATABASE_URL.startswith("postgresql"):
            # PostgreSQL
            db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL"))
        else:
            # Generic SQL
            db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL"))

        db.commit()
        print("✅ is_admin column added successfully")

        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = add_admin_column()
    sys.exit(0 if success else 1)
