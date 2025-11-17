"""
Symptom recording form component for DoctHER application.

Provides UI for recording symptoms with LLM-powered extraction.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st
from sqlalchemy.orm import Session

from database import crud


def parse_symptom_time(symptom_time_data: Optional[Dict[str, Any]]) -> datetime:
    """
    Parse symptom time data from LLM extraction.

    Args:
        symptom_time_data: Dictionary with date and time strings from LLM

    Returns:
        datetime object representing when the symptom occurred
    """
    if not symptom_time_data or symptom_time_data is None:
        # No time mentioned or "now" - use current time
        return datetime.now()

    try:
        date_str = symptom_time_data.get('date')
        time_str = symptom_time_data.get('time')

        if not date_str or not time_str:
            # Missing date or time - use current time
            return datetime.now()

        # Parse the date and time strings
        datetime_str = f"{date_str} {time_str}"
        parsed_time = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        return parsed_time

    except (ValueError, AttributeError, TypeError) as e:
        # If parsing fails, fall back to current time
        st.warning(f"Could not parse symptom time, using current time instead. Error: {e}")
        return datetime.now()


def extract_symptom_fields_with_llm(text: str, client) -> Dict[str, Any]:
    """
    Extract structured symptom fields from natural language using Claude.

    Args:
        text: Natural language symptom description
        client: Anthropic client instance

    Returns:
        Dictionary with extracted fields
    """
    # Get current datetime for context
    current_time = datetime.now()

    extraction_prompt = f"""Extract symptom information from the following text and return a JSON object with these fields:

- symptom_type: Type of symptom (e.g., 'pain', 'bleeding', 'fatigue', 'mood', 'digestive', 'headache')
- body_part: Specific body part or location (e.g., 'abdomen', 'lower back', 'head', 'chest')
- duration: How long the symptom has lasted (e.g., '2 hours', '3 days', 'ongoing')
- severity: Severity on a scale of 1-10 (integer). Convert qualitative descriptions to numeric scores:
  * "mild", "slight", "minor", "light" = 2-3
  * "moderate", "medium", "noticeable" = 4-6
  * "severe", "bad", "serious", "strong" = 7-8
  * "extreme", "unbearable", "worst", "intense", "terrible" = 9-10
  * "very mild" = 1
  * If no severity is mentioned, use null
- symptom_time: When the symptom occurred. Return a JSON object with:
  - relative_time: The relative time phrase from the text (e.g., "yesterday morning", "this afternoon", "2 hours ago", "now", "last night")
  - date: Calculate the ACTUAL date when symptom occurred in YYYY-MM-DD format based on the current date/time provided
    * "yesterday" = subtract 1 day from current date
    * "2 days ago" = subtract 2 days from current date
    * "3 days ago" = subtract 3 days from current date
    * "last week" = subtract 7 days from current date
    * "this morning" = use current date
    * etc.
  - time: Approximate time in HH:MM format (24-hour) when symptom occurred
    * "morning" = 09:00
    * "afternoon" = 15:00
    * "evening" = 19:00
    * "night" = 22:00
    * Use current time for "now" or if no time of day mentioned
  If no time is mentioned or it says "now", use null for this field.
- related_symptoms: Any related or concurrent symptoms (comma-separated list)
- triggers: Possible triggers or causes mentioned (comma-separated list)
- description: A brief summary of the symptom

Context: Current date and time is {current_time.strftime('%Y-%m-%d %H:%M')}

If a field is not mentioned or cannot be determined, use null for that field.

User's symptom description:
{text}

Return ONLY a valid JSON object, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": extraction_prompt}
            ]
        )

        # Extract text from response with validation
        if not response.content:
            st.error("Received empty response from LLM")
            return {}

        # Collect all text content from response
        response_text = ""
        for content in response.content:
            if hasattr(content, 'text'):
                response_text += content.text

        response_text = response_text.strip()

        if not response_text:
            st.error("LLM returned empty text")
            return {}

        # Strip markdown code blocks if present (Claude sometimes wraps JSON in ```)
        if response_text.startswith("```"):
            # Find the actual JSON content between code fences
            lines = response_text.split('\n')
            # Remove first line (```json or ```)
            if len(lines) > 1:
                lines = lines[1:]
            # Remove last line if it's just ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = '\n'.join(lines).strip()

        # Try to parse JSON
        extracted_data = json.loads(response_text)

        return extracted_data

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse LLM response: {e}")
        return {}
    except Exception as e:
        st.error(f"Error extracting symptom fields: {e}")
        return {}


def validate_required_fields(extracted_data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate that required fields are present.

    Args:
        extracted_data: Extracted symptom data

    Returns:
        Tuple of (is_valid, list_of_missing_fields)
    """
    required_fields = ['symptom_type', 'body_part', 'duration', 'severity']
    missing_fields = []

    for field in required_fields:
        if field not in extracted_data or extracted_data[field] is None or extracted_data[field] == "":
            missing_fields.append(field)

    return len(missing_fields) == 0, missing_fields


def show_symptom_recording_form(db_session: Session, client):
    """
    Display symptom recording form with LLM extraction.

    Args:
        db_session: SQLAlchemy database session
        client: Anthropic client instance
    """
    # iOS Safari button fix for regular buttons (non-form)
    st.markdown("""
        <style>
        /* Fix for iOS Safari regular buttons */
        .stButton > button {
            -webkit-appearance: none !important;
            appearance: none !important;
            font-size: 16px !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
        }

        .stButton > button[kind="primary"] {
            background-color: #ff4b4b !important;
            color: white !important;
            border: 1px solid #ff4b4b !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #ff2b2b !important;
            border: 1px solid #ff2b2b !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if we have text to record from main input
    symptom_text = st.session_state.get('symptom_text_to_record', '')

    if not symptom_text:
        st.error("No symptom text found. Please enter your symptom in the main chat box and click Record Symptom.")
        if st.button("←", type="primary", help="Back to Chat"):
            st.session_state.show_symptom_form = False
            st.rerun()
        return

    # Check if we have cached extraction
    if st.session_state.symptom_extraction_cache is None:
        # Perform extraction and cache it
        with st.spinner("Analyzing your symptom..."):
            extracted_data = extract_symptom_fields_with_llm(symptom_text, client)
            st.session_state.symptom_extraction_cache = extracted_data

    extracted_data = st.session_state.symptom_extraction_cache

    if not extracted_data:
        st.error("Failed to extract symptom information. Please try again.")
        if st.button("←", type="primary", help="Back to Chat"):
            st.session_state.show_symptom_form = False
            st.session_state.symptom_extraction_cache = None
            st.session_state.symptom_text_to_record = None
            st.rerun()
        return

    # Check if required fields are present
    is_valid, missing_fields = validate_required_fields(extracted_data)

    if not is_valid:
        # Show form to collect missing required fields
        st.markdown("### 🩹 Complete Symptom Information")
        st.info(f"**Your description:** {symptom_text}")
        st.warning(f"Some required information is missing: {', '.join(missing_fields)}")
        st.markdown("##### Please provide the missing information:")

        # Show form to fill in missing fields
        show_missing_fields_form(
            db_session, symptom_text, extracted_data, missing_fields
        )
    else:
        # All required fields are present - auto-save to database
        save_symptom(db_session, symptom_text, extracted_data)

        # Show success message with extracted information
        st.markdown("### ✅ Symptom Saved Successfully!")

        st.info(f"**Your description:** {symptom_text}")

        st.markdown("#### Saved Information:")

        # Parse and display symptom time
        symptom_time_data = extracted_data.get('symptom_time')
        parsed_time = parse_symptom_time(symptom_time_data)
        time_display = parsed_time.strftime('%Y-%m-%d %H:%M')
        if symptom_time_data:
            relative_time = symptom_time_data.get('relative_time', 'now')
            time_display = f"{time_display} ({relative_time})"

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Type:** {extracted_data.get('symptom_type', 'N/A')}")
            st.markdown(f"**Location:** {extracted_data.get('body_part', 'N/A')}")
            st.markdown(f"**Duration:** {extracted_data.get('duration', 'N/A')}")
            st.markdown(f"**Time:** {time_display}")
        with col2:
            st.markdown(f"**Severity:** {extracted_data.get('severity', 'N/A')}/10" if extracted_data.get('severity') else "**Severity:** N/A")
            st.markdown(f"**Related Symptoms:** {extracted_data.get('related_symptoms', 'None')}")
            st.markdown(f"**Triggers:** {extracted_data.get('triggers', 'None')}")

        # Back to chat button
        if st.button("←", type="primary", help="Back to Chat"):
            # Clear cache and state
            st.session_state.symptom_extraction_cache = None
            st.session_state.symptom_text_to_record = None
            st.session_state.show_symptom_form = False
            st.rerun()


def show_missing_fields_form(
    db_session: Session,
    original_text: str,
    extracted_data: Dict[str, Any],
    missing_fields: list[str]
):
    """
    Show form to fill in missing required fields.

    Args:
        db_session: SQLAlchemy database session
        original_text: Original symptom description
        extracted_data: Partially extracted data
        missing_fields: List of missing field names
    """
    st.markdown("#### Complete Missing Information")

    # iOS Safari button fix
    st.markdown("""
        <style>
        /* Fix for iOS Safari and general button rendering */
        div[data-testid="stForm"] button {
            -webkit-appearance: none !important;
            appearance: none !important;
            font-size: 16px !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
        }

        /* Primary buttons */
        div[data-testid="stForm"] button:first-of-type,
        div[data-testid="stForm"] button[kind="primary"] {
            background-color: #ff4b4b !important;
            color: white !important;
            border: 1px solid #ff4b4b !important;
        }

        div[data-testid="stForm"] button:first-of-type:hover,
        div[data-testid="stForm"] button[kind="primary"]:hover {
            background-color: #ff2b2b !important;
            border: 1px solid #ff2b2b !important;
        }

        /* Secondary buttons */
        div[data-testid="stForm"] button:nth-of-type(2),
        div[data-testid="stForm"] button[kind="secondary"] {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
            border: 1px solid #d4d4d4 !important;
        }

        div[data-testid="stForm"] button:nth-of-type(2):hover,
        div[data-testid="stForm"] button[kind="secondary"]:hover {
            background-color: #e0e2e6 !important;
            border: 1px solid #c4c4c4 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("missing_fields_form"):
        # Create inputs for missing fields - capture values to temporary variables
        form_symptom_type = None
        form_body_part = None
        form_duration = None
        form_severity = None

        if 'symptom_type' in missing_fields:
            form_symptom_type = st.text_input(
                "Symptom Type*",
                placeholder="e.g., pain, bleeding, fatigue"
            )

        if 'body_part' in missing_fields:
            form_body_part = st.text_input(
                "Body Part / Location*",
                placeholder="e.g., abdomen, lower back, head"
            )

        if 'duration' in missing_fields:
            form_duration = st.text_input(
                "Duration*",
                placeholder="e.g., 2 hours, 3 days, ongoing"
            )

        if 'severity' in missing_fields:
            form_severity = st.selectbox(
                "Severity* (1-10)",
                options=list(range(1, 11)),
                index=4,  # Default to 5 (index 4 in 1-10 range)
                help="Rate the severity of your symptom from 1 (mild) to 10 (severe)"
            )

        col1, col2 = st.columns([1, 1])

        with col1:
            submitted = st.form_submit_button("✅ Save Symptom", type="primary", use_container_width=True)

        with col2:
            canceled = st.form_submit_button("❌ Cancel", use_container_width=True)

    # Handle form submission outside the form context
    if canceled:
        # Clear cache and state
        st.session_state.symptom_extraction_cache = None
        st.session_state.symptom_text_to_record = None
        st.session_state.show_symptom_form = False
        st.rerun()

    if submitted:
        # Update extracted_data with form values
        if form_symptom_type is not None:
            extracted_data['symptom_type'] = form_symptom_type
        if form_body_part is not None:
            extracted_data['body_part'] = form_body_part
        if form_duration is not None:
            extracted_data['duration'] = form_duration
        if form_severity is not None:
            extracted_data['severity'] = form_severity

        # Validate again
        is_valid, still_missing = validate_required_fields(extracted_data)

        if is_valid:
            save_symptom(db_session, original_text, extracted_data)
            # Clear cache and state
            st.session_state.symptom_extraction_cache = None
            st.session_state.symptom_text_to_record = None
            st.session_state.show_symptom_form = False
            st.success("✅ Symptom saved successfully!")
            st.rerun()
        else:
            st.error(f"Please fill in all required fields: {', '.join(still_missing)}")


def save_symptom(db_session: Session, original_text: str, extracted_data: Dict[str, Any]):
    """
    Save symptom to database.

    Args:
        db_session: SQLAlchemy database session
        original_text: Original symptom description
        extracted_data: Extracted symptom fields
    """
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User not authenticated")
        return

    try:
        # Parse symptom time from extracted data
        symptom_time_data = extracted_data.get('symptom_time')
        parsed_time = parse_symptom_time(symptom_time_data)

        # Create symptom record
        symptom = crud.create_symptom(
            db_session,
            user_id=user_id,
            symptom_type=extracted_data.get('symptom_type'),
            body_part=extracted_data.get('body_part'),
            duration=extracted_data.get('duration'),
            symptom_time=parsed_time,
            severity=extracted_data.get('severity'),
            description=original_text,  # Save raw user input as description
            related_symptoms=extracted_data.get('related_symptoms'),
            triggers=extracted_data.get('triggers'),
            raw_input=original_text,
            extraction_data=json.dumps(extracted_data),
        )

        # Note: Success message is shown by the caller
        # Clear the form
        if 'symptom_input' in st.session_state:
            del st.session_state.symptom_input

        return symptom

    except Exception as e:
        st.error(f"Error saving symptom: {e}")
