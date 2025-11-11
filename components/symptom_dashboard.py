"""
Symptom dashboard and visualization component for DoctHER application.

Provides symptom tracking tables and time-series visualizations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session

from database import crud
from database.models import Symptom
import re


def parse_duration_to_hours(duration_str: str) -> Optional[float]:
    """
    Parse duration string to hours for visualization.

    Args:
        duration_str: Duration string like "2 hours", "3 days", "ongoing"

    Returns:
        Duration in hours or None if unparseable
    """
    if not duration_str or duration_str.lower() in ['unknown', 'ongoing', 'n/a']:
        return None

    duration_str = duration_str.lower().strip()

    # Try to extract number and unit
    # Patterns: "2 hours", "3 days", "1.5 hours", "2-3 hours"
    patterns = [
        r'(\d+\.?\d*)\s*(?:hour|hr|h)s?',  # hours
        r'(\d+\.?\d*)\s*(?:day|d)s?',      # days
        r'(\d+\.?\d*)\s*(?:week|wk|w)s?',  # weeks
        r'(\d+\.?\d*)\s*(?:minute|min|m)s?', # minutes
    ]

    for pattern in patterns:
        match = re.search(pattern, duration_str)
        if match:
            value = float(match.group(1))

            # Convert to hours based on unit
            if 'hour' in pattern or 'hr' in pattern or 'h' in pattern:
                return value
            elif 'day' in pattern or 'd' in pattern:
                return value * 24
            elif 'week' in pattern or 'wk' in pattern or 'w' in pattern:
                return value * 24 * 7
            elif 'minute' in pattern or 'min' in pattern or 'm' in pattern:
                return value / 60

    return None


def show_symptom_dashboard(db_session: Session):
    """
    Display symptom tracking dashboard with tables and visualizations.

    Args:
        db_session: SQLAlchemy database session
    """
    st.markdown("# 📋 Symptom Tracker")

    # Initialize insights view state
    if 'show_insights_for' not in st.session_state:
        st.session_state.show_insights_for = None

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User not authenticated")
        return

    # Get symptom types for the user
    symptom_types = crud.get_symptom_types_for_user(db_session, user_id)

    if not symptom_types:
        st.info("No symptoms recorded yet. Use the 'Record Symptom' button in the chat to start tracking.")

        if st.button("←", help="Back to Chat"):
            st.session_state.show_symptom_tracker = False
            st.session_state.show_insights_for = None
            st.rerun()
        return

    # Date range filter
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        start_date = st.date_input(
            "From Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now()
        )

    with col2:
        end_date = st.date_input(
            "To Date",
            value=datetime.now(),
            max_value=datetime.now()
        )

    with col3:
        if st.button("←", help="Back to Chat"):
            st.session_state.show_symptom_tracker = False
            st.session_state.show_insights_for = None
            st.rerun()

    st.markdown("---")

    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Check if we're showing insights for a specific symptom type
    if 'show_insights_for' in st.session_state and st.session_state.show_insights_for:
        symptom_type = st.session_state.show_insights_for

        # Get symptoms for this type
        symptoms = crud.get_user_symptoms(
            db_session,
            user_id,
            symptom_type=symptom_type,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=100
        )

        # Back button to return to symptom list - icon only with hover text
        if st.button("←", key="back_from_insights", help="Back to Symptom List"):
            st.session_state.show_insights_for = None
            st.rerun()

        st.markdown("---")

        # Show insights view (not nested in expander)
        show_symptom_insights(db_session, symptom_type, symptoms)

    else:
        # Display symptoms by type (default view)
        for symptom_type in symptom_types:
            with st.expander(f"### {symptom_type.title()}", expanded=True):
                # Get symptoms for this type
                symptoms = crud.get_user_symptoms(
                    db_session,
                    user_id,
                    symptom_type=symptom_type,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    limit=100
                )

                if symptoms:
                    # Show statistics
                    stats = crud.get_symptom_stats(db_session, user_id, symptom_type)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Total Occurrences", stats['total_count'])

                    with col2:
                        if stats['avg_severity']:
                            st.metric("Average Severity", f"{stats['avg_severity']}/10")
                        else:
                            st.metric("Average Severity", "N/A")

                    # Insights button - icon only with tooltip on hover - above table
                    if st.button("📈", key=f"insights_{symptom_type}", help="View Insights"):
                        st.session_state.show_insights_for = symptom_type
                        st.rerun()

                    # Show symptoms table
                    st.markdown("#### Recent Symptoms")
                    display_symptom_table(db_session, symptoms)

                else:
                    st.info(f"No {symptom_type} symptoms recorded in this date range.")


def display_symptom_table(db_session: Session, symptoms: List[Symptom]):
    """
    Display symptoms in a formatted table with delete buttons.

    Args:
        db_session: SQLAlchemy database session
        symptoms: List of symptom records
    """
    if not symptoms:
        st.info("No symptoms to display")
        return

    # Display column headers
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 1, 3, 0.5])
    with col1:
        st.markdown("**Date & Time**")
    with col2:
        st.markdown("**Location**")
    with col3:
        st.markdown("**Duration**")
    with col4:
        st.markdown("**Severity**")
    with col5:
        st.markdown("**Description**")
    with col6:
        st.markdown("")  # For delete button column

    st.markdown("---")

    # Display each symptom as a row with delete button
    for symptom in symptoms:
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 1, 3, 0.5])

        with col1:
            st.markdown(f"**{symptom.symptom_time.strftime('%Y-%m-%d %H:%M')}**")

        with col2:
            st.markdown(f"{symptom.body_part or 'N/A'}")

        with col3:
            st.markdown(f"{symptom.duration or 'N/A'}")

        with col4:
            severity_text = f"{symptom.severity}/10" if symptom.severity else "N/A"
            st.markdown(f"{severity_text}")

        with col5:
            description = symptom.description or symptom.raw_input or "N/A"
            if len(description) > 50:
                description = description[:50] + "..."
            st.markdown(f"_{description}_")

        with col6:
            # Delete button - no confirmation
            if st.button("🗑️", key=f"delete_{symptom.id}", help="Delete symptom"):
                if crud.delete_symptom(db_session, symptom.id):
                    st.rerun()
                else:
                    st.error("Failed to delete symptom")

        st.markdown("---")


def show_symptom_insights(db_session: Session, symptom_type: str, symptoms: List[Symptom]):
    """
    Show visualizations and insights for a specific symptom type, grouped by location.

    Args:
        db_session: SQLAlchemy database session
        symptom_type: Type of symptom to visualize
        symptoms: List of symptom records
    """
    st.markdown(f"#### 📈 Insights: {symptom_type.title()}")

    # Prepare data for visualization
    dates = []
    severities = []
    locations = []
    durations = []
    duration_hours = []
    times_of_day = []

    for symptom in sorted(symptoms, key=lambda x: x.symptom_time):
        dates.append(symptom.symptom_time)
        severities.append(symptom.severity if symptom.severity else None)
        locations.append(symptom.body_part or "Unknown")
        duration_str = symptom.duration or "Unknown"
        durations.append(duration_str)
        # Parse duration to hours for numeric analysis
        duration_hours.append(parse_duration_to_hours(duration_str))
        # Extract hour of day for time-of-day analysis
        times_of_day.append(symptom.symptom_time.hour)

    # Create DataFrame
    df = pd.DataFrame({
        "Date": dates,
        "Severity": severities,
        "Location": locations,
        "Duration": durations,
        "DurationHours": duration_hours,
        "Hour": times_of_day
    })

    # Remove rows with no severity data
    df_with_severity = df[df['Severity'].notna()]

    if df_with_severity.empty:
        st.info("No severity data available for visualization. Severity information was not recorded for these symptoms.")
        return

    # Overall statistics
    st.markdown("##### Overall Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Entries", len(df_with_severity))

    with col2:
        st.metric("Average Severity", f"{df_with_severity['Severity'].mean():.1f}/10")

    with col3:
        st.metric("Max Severity", f"{df_with_severity['Severity'].max():.1f}/10")

    st.markdown("---")

    # Severity Over Time Chart
    st.markdown("**Severity Over Time**")

    fig_dates = go.Figure()

    fig_dates.add_trace(go.Scatter(
        x=df_with_severity['Date'],
        y=df_with_severity['Severity'],
        mode='lines+markers',
        name='Severity',
        line=dict(color='#2C8C99', width=2),
        marker=dict(size=8),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br><b>Severity:</b> %{y}/10<extra></extra>'
    ))

    fig_dates.update_layout(
        xaxis_title="Date",
        yaxis_title="Severity (1-10)",
        yaxis=dict(range=[0, 10]),
        hovermode='x unified',
        height=350,
        template="plotly_white",
        margin=dict(l=40, r=40, t=20, b=40)
    )

    st.plotly_chart(fig_dates, use_container_width=True)

    # Symptom by Location Chart
    st.markdown("**Symptoms by Location**")

    # Count occurrences by location
    location_counts = df_with_severity['Location'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Count']

    fig_location = go.Figure()

    fig_location.add_trace(go.Bar(
        x=location_counts['Location'],
        y=location_counts['Count'],
        marker=dict(color='#9b6b8e'),
        hovertemplate='<b>Location:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>'
    ))

    fig_location.update_layout(
        xaxis_title="Body Location",
        yaxis_title="Number of Occurrences",
        height=350,
        template="plotly_white",
        margin=dict(l=40, r=40, t=20, b=40)
    )

    st.plotly_chart(fig_location, use_container_width=True)

    # Severity by Time of Day Chart
    st.markdown("**Severity by Time of Day**")

    # Group by hour and calculate average severity
    hourly_severity = df_with_severity.groupby('Hour')['Severity'].mean().reset_index()

    fig_time = go.Figure()

    fig_time.add_trace(go.Bar(
        x=hourly_severity['Hour'],
        y=hourly_severity['Severity'],
        marker=dict(color='#6b8e7f'),
        hovertemplate='<b>Hour:</b> %{x}:00<br><b>Avg Severity:</b> %{y:.1f}/10<extra></extra>'
    ))

    fig_time.update_layout(
        xaxis_title="Hour of Day (24h)",
        yaxis_title="Average Severity (1-10)",
        yaxis=dict(range=[0, 10]),
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        ),
        height=350,
        template="plotly_white",
        margin=dict(l=40, r=40, t=20, b=40)
    )

    st.plotly_chart(fig_time, use_container_width=True)

    # Duration by Time of Day Chart
    st.markdown("**Duration by Time of Day**")

    # Filter to only include parseable durations
    df_with_duration = df_with_severity[df_with_severity['DurationHours'].notna()]

    if not df_with_duration.empty:
        # Group by hour and calculate average duration in hours
        hourly_duration = df_with_duration.groupby('Hour')['DurationHours'].mean().reset_index()

        fig_duration = go.Figure()

        fig_duration.add_trace(go.Bar(
            x=hourly_duration['Hour'],
            y=hourly_duration['DurationHours'],
            marker=dict(color='#d4a24c'),
            hovertemplate='<b>Hour:</b> %{x}:00<br><b>Avg Duration:</b> %{y:.1f} hours<extra></extra>'
        ))

        fig_duration.update_layout(
            xaxis_title="Hour of Day (24h)",
            yaxis_title="Average Duration (hours)",
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=2,
                range=[-0.5, 23.5]
            ),
            height=350,
            template="plotly_white",
            margin=dict(l=40, r=40, t=20, b=40)
        )

        st.plotly_chart(fig_duration, use_container_width=True)
    else:
        st.info("No parseable duration data available. Duration should include time units (e.g., '2 hours', '3 days').")

    # Export data option
    if st.button("📥 Export Data (CSV)", key=f"export_{symptom_type}"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"symptom_{symptom_type}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
