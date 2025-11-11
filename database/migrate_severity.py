#!/usr/bin/env python3
"""
Migration script to update NULL severity values to default (5).

This script updates all existing symptom records that have NULL severity
to a default value of 5 on a 1-10 scale.

Usage:
    python -m database.migrate_severity
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database import init_db, get_session_maker, crud


def main():
    """Run the severity migration."""
    print("=" * 60)
    print("Severity Migration Script")
    print("=" * 60)
    print()

    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./womens_health_mcp.db")
    print(f"Database: {database_url}")
    print()

    # Initialize database connection
    print("Connecting to database...")
    engine = init_db(database_url)
    SessionLocal = get_session_maker(engine)

    # Create session
    db = SessionLocal()

    try:
        print("Checking for symptoms with NULL severity...")
        print()

        # Run the update
        updated_count = crud.update_null_severities_to_default(db, default_severity=5)

        print("=" * 60)
        if updated_count > 0:
            print(f"✅ Successfully updated {updated_count} symptom record(s)")
            print(f"   All NULL severity values set to: 5")
        else:
            print("ℹ️  No symptoms found with NULL severity")
            print("   All symptom records already have severity values")
        print("=" * 60)
        print()
        print("Migration completed successfully!")

    except Exception as e:
        print("=" * 60)
        print(f"❌ Error during migration: {e}")
        print("=" * 60)
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
