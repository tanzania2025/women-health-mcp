#!/usr/bin/env python3
"""
Script to populate demo symptom data for demo@docther.com account.

Usage:
    python -m scripts.populate_demo_data
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database import init_db, get_session_maker, crud
from auth import Authenticator


def create_demo_user(db_session, authenticator):
    """Create or get demo user."""
    email = "demo@docther.com"

    # Check if user exists
    user = crud.get_user_by_email(db_session, email)

    if not user:
        # Create demo user with password "demo123"
        password_hash = authenticator.hash_password("demo123")
        user = crud.create_user(
            db_session,
            email=email,
            password_hash=password_hash,
            username="demo"
        )
        print(f"✅ Created demo user: {email}")
    else:
        print(f"ℹ️  Demo user already exists: {email}")

    return user


def populate_symptom_data(db_session, user_id):
    """Populate realistic symptom data for demo - 3 months of data."""

    print("\n📊 Creating demo symptom data (3 months)...")

    # Demo symptoms with realistic data spanning 90 days
    symptoms_data = [
        # Headaches - spread over 3 months
        {
            "symptom_type": "headache",
            "body_part": "temples",
            "duration": "3 hours",
            "days_ago": 2,
            "hour": 14,
            "severity": 7,
            "description": "Sharp headache at temples, started after lunch",
            "related_symptoms": "light sensitivity",
            "triggers": "stress, lack of sleep"
        },
        {
            "symptom_type": "headache",
            "body_part": "forehead",
            "duration": "2 hours",
            "days_ago": 5,
            "hour": 9,
            "severity": 5,
            "description": "Dull headache in forehead area, morning onset",
            "related_symptoms": None,
            "triggers": "dehydration"
        },
        {
            "symptom_type": "headache",
            "body_part": "back of head",
            "duration": "4 hours",
            "days_ago": 10,
            "hour": 16,
            "severity": 8,
            "description": "Severe throbbing headache, back of head",
            "related_symptoms": "nausea",
            "triggers": "screen time"
        },
        {
            "symptom_type": "headache",
            "body_part": "temples",
            "duration": "1.5 hours",
            "days_ago": 15,
            "hour": 11,
            "severity": 4,
            "description": "Mild pressure headache at temples",
            "related_symptoms": None,
            "triggers": None
        },
        {
            "symptom_type": "headache",
            "body_part": "forehead",
            "duration": "5 hours",
            "days_ago": 20,
            "hour": 19,
            "severity": 9,
            "description": "Intense migraine, forehead and temples, very painful",
            "related_symptoms": "nausea, light sensitivity",
            "triggers": "hormonal changes"
        },

        # Abdominal pain
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "2 hours",
            "days_ago": 1,
            "hour": 8,
            "severity": 6,
            "description": "Cramping pain in lower abdomen, morning",
            "related_symptoms": "bloating",
            "triggers": None
        },
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "4 hours",
            "days_ago": 7,
            "hour": 10,
            "severity": 8,
            "description": "Sharp cramping pain, lower abdomen",
            "related_symptoms": "fatigue",
            "triggers": "menstrual cycle"
        },
        {
            "symptom_type": "pain",
            "body_part": "upper abdomen",
            "duration": "1 hour",
            "days_ago": 12,
            "hour": 13,
            "severity": 4,
            "description": "Mild discomfort after eating",
            "related_symptoms": "bloating",
            "triggers": "spicy food"
        },

        # Fatigue
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "all day",
            "days_ago": 3,
            "hour": 7,
            "severity": 7,
            "description": "Extreme tiredness throughout the day, couldn't concentrate",
            "related_symptoms": "difficulty concentrating",
            "triggers": "poor sleep"
        },
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "afternoon",
            "days_ago": 8,
            "hour": 14,
            "severity": 5,
            "description": "Afternoon energy crash, needed to rest",
            "related_symptoms": None,
            "triggers": None
        },
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "all day",
            "days_ago": 14,
            "hour": 8,
            "severity": 8,
            "description": "Overwhelming exhaustion, could barely function",
            "related_symptoms": "brain fog",
            "triggers": "stress"
        },

        # Back pain
        {
            "symptom_type": "pain",
            "body_part": "lower back",
            "duration": "6 hours",
            "days_ago": 4,
            "hour": 15,
            "severity": 6,
            "description": "Aching lower back pain, worsened when sitting",
            "related_symptoms": None,
            "triggers": "poor posture"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower back",
            "duration": "3 hours",
            "days_ago": 11,
            "hour": 9,
            "severity": 7,
            "description": "Sharp pain in lower back, difficulty moving",
            "related_symptoms": "muscle stiffness",
            "triggers": "exercise"
        },

        # Mood symptoms
        {
            "symptom_type": "mood",
            "body_part": None,
            "duration": "all day",
            "days_ago": 6,
            "hour": 10,
            "severity": 6,
            "description": "Feeling anxious and irritable throughout the day",
            "related_symptoms": "difficulty sleeping",
            "triggers": "hormonal changes"
        },
        {
            "symptom_type": "mood",
            "body_part": None,
            "duration": "evening",
            "days_ago": 13,
            "hour": 18,
            "severity": 7,
            "description": "Low mood in the evening, felt sad and tearful",
            "related_symptoms": "loss of appetite",
            "triggers": "stress"
        },

        # Joint pain
        {
            "symptom_type": "pain",
            "body_part": "knee",
            "duration": "2 hours",
            "days_ago": 9,
            "hour": 16,
            "severity": 5,
            "description": "Dull ache in right knee after walking",
            "related_symptoms": "stiffness",
            "triggers": "exercise"
        },

        # Additional headaches going back 3 months
        {
            "symptom_type": "headache",
            "body_part": "temples",
            "duration": "2.5 hours",
            "days_ago": 25,
            "hour": 13,
            "severity": 6,
            "description": "Moderate headache at temples, afternoon",
            "related_symptoms": None,
            "triggers": "caffeine withdrawal"
        },
        {
            "symptom_type": "headache",
            "body_part": "forehead",
            "duration": "4 hours",
            "days_ago": 32,
            "hour": 10,
            "severity": 7,
            "description": "Persistent headache across forehead",
            "related_symptoms": "light sensitivity",
            "triggers": "stress"
        },
        {
            "symptom_type": "headache",
            "body_part": "back of head",
            "duration": "3 hours",
            "days_ago": 38,
            "hour": 15,
            "severity": 5,
            "description": "Tension headache at back of head",
            "related_symptoms": "neck stiffness",
            "triggers": "poor posture"
        },
        {
            "symptom_type": "headache",
            "body_part": "temples",
            "duration": "6 hours",
            "days_ago": 45,
            "hour": 8,
            "severity": 9,
            "description": "Severe migraine, temples throbbing",
            "related_symptoms": "nausea, light sensitivity, dizziness",
            "triggers": "hormonal changes"
        },
        {
            "symptom_type": "headache",
            "body_part": "forehead",
            "duration": "2 hours",
            "days_ago": 52,
            "hour": 14,
            "severity": 4,
            "description": "Mild headache after skipping lunch",
            "related_symptoms": None,
            "triggers": "hunger"
        },
        {
            "symptom_type": "headache",
            "body_part": "temples",
            "duration": "3.5 hours",
            "days_ago": 60,
            "hour": 11,
            "severity": 6,
            "description": "Moderate pressure headache, temples",
            "related_symptoms": None,
            "triggers": "weather changes"
        },
        {
            "symptom_type": "headache",
            "body_part": "back of head",
            "duration": "5 hours",
            "days_ago": 67,
            "hour": 17,
            "severity": 8,
            "description": "Intense headache at back of head and neck",
            "related_symptoms": "neck pain",
            "triggers": "stress, tension"
        },
        {
            "symptom_type": "headache",
            "body_part": "forehead",
            "duration": "2.5 hours",
            "days_ago": 75,
            "hour": 9,
            "severity": 5,
            "description": "Morning headache across forehead",
            "related_symptoms": None,
            "triggers": "poor sleep"
        },
        {
            "symptom_type": "headache",
            "body_part": "temples",
            "duration": "4 hours",
            "days_ago": 82,
            "hour": 16,
            "severity": 7,
            "description": "Sharp headache at temples, evening",
            "related_symptoms": "light sensitivity",
            "triggers": "screen time"
        },
        {
            "symptom_type": "headache",
            "body_part": "forehead",
            "duration": "3 hours",
            "days_ago": 88,
            "hour": 12,
            "severity": 6,
            "description": "Persistent forehead headache",
            "related_symptoms": "fatigue",
            "triggers": "dehydration"
        },

        # Additional abdominal pain
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "3 hours",
            "days_ago": 28,
            "hour": 9,
            "severity": 7,
            "description": "Cramping pain, lower abdomen",
            "related_symptoms": "bloating",
            "triggers": "menstrual cycle"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "5 hours",
            "days_ago": 35,
            "hour": 7,
            "severity": 8,
            "description": "Severe cramping, lower abdomen, morning",
            "related_symptoms": "fatigue, nausea",
            "triggers": "menstrual cycle"
        },
        {
            "symptom_type": "pain",
            "body_part": "upper abdomen",
            "duration": "1.5 hours",
            "days_ago": 42,
            "hour": 13,
            "severity": 5,
            "description": "Discomfort in upper abdomen after eating",
            "related_symptoms": "bloating",
            "triggers": "fatty food"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "4 hours",
            "days_ago": 56,
            "hour": 8,
            "severity": 7,
            "description": "Sharp cramping pain, lower abdomen",
            "related_symptoms": "bloating, fatigue",
            "triggers": "menstrual cycle"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "3 hours",
            "days_ago": 63,
            "hour": 10,
            "severity": 6,
            "description": "Moderate cramping, lower abdomen",
            "related_symptoms": "bloating",
            "triggers": "menstrual cycle"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower abdomen",
            "duration": "6 hours",
            "days_ago": 84,
            "hour": 7,
            "severity": 9,
            "description": "Intense cramping pain, very painful",
            "related_symptoms": "nausea, fatigue",
            "triggers": "menstrual cycle"
        },

        # Additional fatigue
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "all day",
            "days_ago": 21,
            "hour": 8,
            "severity": 6,
            "description": "Persistent tiredness throughout the day",
            "related_symptoms": "difficulty concentrating",
            "triggers": "poor sleep"
        },
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "afternoon",
            "days_ago": 36,
            "hour": 15,
            "severity": 7,
            "description": "Severe afternoon fatigue, needed to lie down",
            "related_symptoms": "brain fog",
            "triggers": "stress"
        },
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "all day",
            "days_ago": 49,
            "hour": 7,
            "severity": 8,
            "description": "Extreme exhaustion, could barely get out of bed",
            "related_symptoms": "muscle weakness",
            "triggers": "illness"
        },
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "afternoon",
            "days_ago": 64,
            "hour": 14,
            "severity": 6,
            "description": "Afternoon tiredness, energy crash",
            "related_symptoms": None,
            "triggers": None
        },
        {
            "symptom_type": "fatigue",
            "body_part": None,
            "duration": "all day",
            "days_ago": 78,
            "hour": 8,
            "severity": 7,
            "description": "Persistent fatigue throughout day",
            "related_symptoms": "difficulty concentrating",
            "triggers": "poor sleep"
        },

        # Additional back pain
        {
            "symptom_type": "pain",
            "body_part": "lower back",
            "duration": "4 hours",
            "days_ago": 18,
            "hour": 16,
            "severity": 5,
            "description": "Dull ache in lower back",
            "related_symptoms": None,
            "triggers": "sitting too long"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower back",
            "duration": "5 hours",
            "days_ago": 41,
            "hour": 10,
            "severity": 7,
            "description": "Sharp lower back pain, difficulty bending",
            "related_symptoms": "muscle stiffness",
            "triggers": "exercise"
        },
        {
            "symptom_type": "pain",
            "body_part": "lower back",
            "duration": "3 hours",
            "days_ago": 55,
            "hour": 14,
            "severity": 6,
            "description": "Aching lower back pain",
            "related_symptoms": None,
            "triggers": "poor posture"
        },
        {
            "symptom_type": "pain",
            "body_part": "upper back",
            "duration": "2 hours",
            "days_ago": 71,
            "hour": 11,
            "severity": 5,
            "description": "Tension in upper back and shoulders",
            "related_symptoms": "neck stiffness",
            "triggers": "stress"
        },

        # Additional mood symptoms
        {
            "symptom_type": "mood",
            "body_part": None,
            "duration": "all day",
            "days_ago": 34,
            "hour": 9,
            "severity": 7,
            "description": "Feeling very anxious and on edge all day",
            "related_symptoms": "difficulty sleeping, racing thoughts",
            "triggers": "hormonal changes"
        },
        {
            "symptom_type": "mood",
            "body_part": None,
            "duration": "evening",
            "days_ago": 48,
            "hour": 18,
            "severity": 6,
            "description": "Low mood and irritability in evening",
            "related_symptoms": None,
            "triggers": "stress"
        },
        {
            "symptom_type": "mood",
            "body_part": None,
            "duration": "all day",
            "days_ago": 62,
            "hour": 10,
            "severity": 8,
            "description": "Very low mood, feeling hopeless",
            "related_symptoms": "loss of appetite, fatigue",
            "triggers": "hormonal changes"
        },
        {
            "symptom_type": "mood",
            "body_part": None,
            "duration": "afternoon",
            "days_ago": 76,
            "hour": 15,
            "severity": 5,
            "description": "Feeling irritable and short-tempered",
            "related_symptoms": None,
            "triggers": "stress"
        },

        # Additional joint pain
        {
            "symptom_type": "pain",
            "body_part": "knee",
            "duration": "3 hours",
            "days_ago": 30,
            "hour": 17,
            "severity": 6,
            "description": "Aching right knee, worse after exercise",
            "related_symptoms": "stiffness",
            "triggers": "running"
        },
        {
            "symptom_type": "pain",
            "body_part": "wrist",
            "duration": "2 hours",
            "days_ago": 44,
            "hour": 14,
            "severity": 4,
            "description": "Mild wrist pain from typing",
            "related_symptoms": "stiffness",
            "triggers": "repetitive motion"
        },
        {
            "symptom_type": "pain",
            "body_part": "ankle",
            "duration": "4 hours",
            "days_ago": 58,
            "hour": 16,
            "severity": 6,
            "description": "Swollen ankle, painful to walk",
            "related_symptoms": "swelling",
            "triggers": "twisted ankle"
        },
        {
            "symptom_type": "pain",
            "body_part": "knee",
            "duration": "2 hours",
            "days_ago": 70,
            "hour": 15,
            "severity": 5,
            "description": "Dull ache in left knee",
            "related_symptoms": None,
            "triggers": "exercise"
        },

        # Additional digestive symptoms
        {
            "symptom_type": "digestive",
            "body_part": "stomach",
            "duration": "3 hours",
            "days_ago": 17,
            "hour": 11,
            "severity": 5,
            "description": "Stomach discomfort and bloating",
            "related_symptoms": "gas",
            "triggers": "dairy"
        },
        {
            "symptom_type": "digestive",
            "body_part": "stomach",
            "duration": "2 hours",
            "days_ago": 39,
            "hour": 13,
            "severity": 6,
            "description": "Nausea and upset stomach after eating",
            "related_symptoms": None,
            "triggers": "greasy food"
        },
        {
            "symptom_type": "digestive",
            "body_part": "abdomen",
            "duration": "4 hours",
            "days_ago": 53,
            "hour": 10,
            "severity": 7,
            "description": "Severe bloating and discomfort",
            "related_symptoms": "gas, cramping",
            "triggers": "food intolerance"
        },
        {
            "symptom_type": "digestive",
            "body_part": "stomach",
            "duration": "1.5 hours",
            "days_ago": 69,
            "hour": 12,
            "severity": 4,
            "description": "Mild indigestion after lunch",
            "related_symptoms": None,
            "triggers": "eating too fast"
        },
    ]

    created_count = 0
    now = datetime.now()

    for symptom_data in symptoms_data:
        # Calculate symptom time
        symptom_time = now - timedelta(days=symptom_data["days_ago"])
        symptom_time = symptom_time.replace(
            hour=symptom_data["hour"],
            minute=random.randint(0, 59),
            second=0,
            microsecond=0
        )

        # Create symptom
        crud.create_symptom(
            db_session,
            user_id=user_id,
            symptom_type=symptom_data["symptom_type"],
            body_part=symptom_data["body_part"],
            duration=symptom_data["duration"],
            symptom_time=symptom_time,
            severity=symptom_data["severity"],
            description=symptom_data["description"],
            related_symptoms=symptom_data["related_symptoms"],
            triggers=symptom_data["triggers"],
            raw_input=symptom_data["description"],
        )
        created_count += 1

    print(f"✅ Created {created_count} symptom records")


def main():
    """Run the demo data population."""
    print("=" * 60)
    print("DoctHER Demo Data Population Script")
    print("=" * 60)
    print()

    # Initialize database
    print("Connecting to database...")
    database_url = "sqlite:///./womens_health_mcp.db"
    engine = init_db(database_url)
    SessionLocal = get_session_maker(engine)

    # Create session
    db = SessionLocal()
    authenticator = Authenticator(db)

    try:
        # Create/get demo user
        user = create_demo_user(db, authenticator)

        # Populate symptom data
        populate_symptom_data(db, user.id)

        print()
        print("=" * 60)
        print("✅ Demo data population completed successfully!")
        print("=" * 60)
        print()
        print("Demo Account Credentials:")
        print("  Email: demo@docther.com")
        print("  Password: demo123")
        print()
        print("You can now log in and see the demo symptom data!")

    except Exception as e:
        print("=" * 60)
        print(f"❌ Error during demo data population: {e}")
        print("=" * 60)
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
