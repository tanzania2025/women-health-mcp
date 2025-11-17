"""
Authentication UI components for DoctHER application.

Provides login and signup forms with validation.
"""

import streamlit as st
from sqlalchemy.orm import Session
from auth import Authenticator


def show_login_signup_page(db_session: Session):
    """
    Display login/signup page with tabs.

    Args:
        db_session: SQLAlchemy database session
    """
    authenticator = Authenticator(db_session)

    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # App branding
        st.markdown("<h1 style='text-align: center; color: #2C8C99;'>DoctHER</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 1.2em; margin-bottom: 2em;'>"
            "Your Personal Women's Health Assistant</p>",
            unsafe_allow_html=True
        )

        # Create tabs for login and signup
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        # Login Tab
        with tab1:
            st.subheader("Welcome Back")

            st.markdown("""
                <style>
                /* Fix for iOS Safari tab visibility */
                button[data-baseweb="tab"] {
                    -webkit-appearance: none !important;
                    appearance: none !important;
                    font-size: 16px !important;
                    padding: 0.5rem 1.5rem !important;
                    color: #262730 !important;
                    background-color: transparent !important;
                    border: none !important;
                    border-bottom: 2px solid transparent !important;
                }

                button[data-baseweb="tab"][aria-selected="true"] {
                    color: #ff4b4b !important;
                    border-bottom: 2px solid #ff4b4b !important;
                    font-weight: 600 !important;
                }

                button[data-baseweb="tab"]:hover {
                    background-color: rgba(0, 0, 0, 0.05) !important;
                }

                /* Ensure tabs container is visible */
                div[data-baseweb="tab-list"] {
                    display: flex !important;
                    gap: 0.5rem !important;
                    border-bottom: 1px solid #e0e0e0 !important;
                    margin-bottom: 1.5rem !important;
                }

                /* Fix for iOS Safari and general button rendering */
                div[data-testid="stForm"] button {
                    -webkit-appearance: none !important;
                    appearance: none !important;
                    font-size: 16px !important;
                    padding: 0.5rem 1rem !important;
                    border-radius: 0.5rem !important;
                    font-weight: 500 !important;
                }

                /* First button (Login) - primary style */
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

                /* Second button (Demo) - DoctHER brand color */
                div[data-testid="stForm"] button:nth-of-type(2),
                div[data-testid="stForm"] button[kind="secondary"] {
                    background-color: #2C8C99 !important;
                    color: white !important;
                    border: 1px solid #2C8C99 !important;
                }

                div[data-testid="stForm"] button:nth-of-type(2):hover,
                div[data-testid="stForm"] button[kind="secondary"]:hover {
                    background-color: #237680 !important;
                    color: white !important;
                    border: 1px solid #237680 !important;
                }
                </style>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    placeholder="your.email@example.com",
                    key="login_email"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )

                submitted = st.form_submit_button("Login", use_container_width=True)
                demo_submitted = st.form_submit_button("Use Demo Account", use_container_width=True, type="secondary")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password")
                    else:
                        success, message, user = authenticator.login_user(email, password)

                        if success:
                            authenticator.set_user_session(user)
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

                if demo_submitted:
                    success, message, user = authenticator.login_user("demo@docther.com", "demo1234")
                    if success:
                        authenticator.set_user_session(user)
                        st.success("Logged in as demo user!")
                        st.rerun()
                    else:
                        st.error(f"Demo account not available: {message}")

        # Signup Tab
        with tab2:
            st.subheader("Create Your Account")

            with st.form("signup_form"):
                new_email = st.text_input(
                    "Email",
                    placeholder="your.email@example.com",
                    key="signup_email",
                    help="We'll never share your email"
                )
                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Choose a strong password",
                    key="signup_password",
                    help="At least 8 characters, include letters and numbers"
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="signup_confirm_password"
                )

                submitted = st.form_submit_button("Sign Up", use_container_width=True)

                if submitted:
                    # Validation
                    if not all([new_email, new_password, confirm_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message, user = authenticator.register_user(
                            new_email, new_password
                        )

                        if success:
                            # Auto-login after successful registration
                            authenticator.set_user_session(user)
                            st.success(f"{message} Welcome!")
                            st.rerun()
                        else:
                            st.error(message)

        # Footer
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #999; font-size: 0.9em;'>"
            "DoctHER is a health information tool. Always consult with healthcare professionals for medical advice."
            "</p>",
            unsafe_allow_html=True
        )


def show_logout_button(authenticator: Authenticator):
    """
    Display logout button in sidebar.

    Args:
        authenticator: Authenticator instance
    """
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        authenticator.clear_session()
        st.rerun()
