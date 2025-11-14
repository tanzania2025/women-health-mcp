#!/usr/bin/env python3
"""
Migration script to add is_admin column to users table.

Usage: python -m scripts.migrate_add_admin
"""

import os
from dotenv import load_dotenv
from sqlalchemy import text

from database.models import init_db, get_session_maker

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./womens_health_mcp.db")


def add_admin_column():
    """Add is_admin column to users table if it doesn't exist."""
    print("=" * 60)
    print("Database Migration: Add is_admin Column")
    print("=" * 60)

    engine = init_db(DATABASE_URL)
    SessionLocal = get_session_maker(engine)
    db = SessionLocal()

    try:
        # Check if column exists
        if DATABASE_URL.startswith("sqlite"):
            # SQLite check
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]

            if 'is_admin' in columns:
                print("✓ is_admin column already exists")
            else:
                print("Adding is_admin column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL"))
                db.commit()
                print("✅ is_admin column added successfully")

        elif DATABASE_URL.startswith("postgresql"):
            # PostgreSQL check
            result = db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='users' AND column_name='is_admin'
            """))

            if result.fetchone():
                print("✓ is_admin column already exists")
            else:
                print("Adding is_admin column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL"))
                db.commit()
                print("✅ is_admin column added successfully")

        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_admin_column()
