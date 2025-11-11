#!/usr/bin/env python3
"""
Test database connection to verify Supabase PostgreSQL setup.
Usage: python test_db_connection.py
"""

import os
from dotenv import load_dotenv
from database.models import init_db, get_engine, get_session_maker, Base
from sqlalchemy import text

def test_database_connection():
    """Test database connection and table creation."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)

    # Load environment variables
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("   Make sure you have a .env file with DATABASE_URL set")
        return False

    print(f"\n1. Database URL loaded:")
    # Mask password for security (only for PostgreSQL URLs)
    if '@' in database_url:
        masked_url = database_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + database_url.split('@')[1]
    else:
        masked_url = database_url  # SQLite URLs don't have passwords
    print(f"   {masked_url}")

    # Determine database type
    if database_url.startswith("postgresql"):
        print(f"   Database Type: PostgreSQL (Production)")
    else:
        print(f"   Database Type: SQLite (Development)")

    try:
        # Test 1: Create engine
        print("\n2. Creating database engine...")
        engine = get_engine(database_url)
        print("   ✅ Engine created successfully")

        # Test 2: Test connection
        print("\n3. Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("   ✅ Connection successful")

        # Test 3: Create tables
        print("\n4. Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tables created successfully")

        # Test 4: List tables
        print("\n5. Verifying tables exist...")
        with engine.connect() as connection:
            if database_url.startswith("postgresql"):
                # PostgreSQL query
                result = connection.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                ))
            else:
                # SQLite query
                result = connection.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ))

            tables = [row[0] for row in result]
            print(f"   Found {len(tables)} tables:")
            for table in sorted(tables):
                print(f"     - {table}")

        expected_tables = {'users', 'chat_sessions', 'messages', 'tool_logs', 'symptoms'}
        if expected_tables.issubset(set(tables)):
            print("   ✅ All required tables present")
        else:
            missing = expected_tables - set(tables)
            print(f"   ⚠️  Missing tables: {missing}")

        # Test 5: Test session creation
        print("\n6. Testing session creation...")
        SessionLocal = get_session_maker(engine)
        db = SessionLocal()
        db.close()
        print("   ✅ Session created and closed successfully")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Database is ready to use!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Run the app locally: streamlit run demos/doct_her_stdio.py")
        print("  2. Deploy to Streamlit Cloud with these credentials")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify your DATABASE_URL is correct in .env")
        print("  2. Check your database password is correct")
        print("  3. Ensure Supabase project is active (not paused)")
        print("  4. Verify network connectivity to Supabase")

        return False

if __name__ == "__main__":
    success = test_database_connection()
    exit(0 if success else 1)
