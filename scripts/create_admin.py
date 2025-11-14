#!/usr/bin/env python3
"""
Script to promote users to admin status.

Usage: python -m scripts.create_admin
"""

import os
from dotenv import load_dotenv
from database.models import init_db, get_session_maker, User

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./womens_health_mcp.db")

# Admin email addresses
ADMIN_EMAILS = [
    "dangordon@live.co.uk",
    "sunainad.7@gmail.com",
    "demo@docther.com",  # Note: Fixed typo from "docter" to "docther"
]


def promote_users_to_admin():
    """Promote specified users to admin status."""
    print("=" * 60)
    print("Admin User Promotion Script")
    print("=" * 60)

    # Initialize database
    engine = init_db(DATABASE_URL)
    SessionLocal = get_session_maker(engine)
    db = SessionLocal()

    try:
        promoted_count = 0
        not_found = []

        for email in ADMIN_EMAILS:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()

            if user:
                if user.is_admin:
                    print(f"✓ {email} - Already admin")
                else:
                    user.is_admin = True
                    db.commit()
                    promoted_count += 1
                    print(f"✅ {email} - Promoted to admin")
            else:
                not_found.append(email)
                print(f"⚠️  {email} - User not found (needs to sign up first)")

        print("\n" + "=" * 60)
        print(f"Summary:")
        print(f"  - Promoted: {promoted_count}")
        print(f"  - Not found: {len(not_found)}")

        if not_found:
            print(f"\n⚠️  Users not found need to sign up first:")
            for email in not_found:
                print(f"     - {email}")

        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    promote_users_to_admin()
