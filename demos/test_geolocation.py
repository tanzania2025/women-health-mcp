#!/usr/bin/env python3
"""
Test geolocation service.

Simple demo to show user's country based on IP address.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from services.geolocation import get_user_country, get_client_ip

st.set_page_config(
    page_title="IP Geolocation Test",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 IP Geolocation Test")

st.markdown("This tool detects your location based on your IP address.")

if st.button("Detect My Location"):
    with st.spinner("Detecting location..."):
        # Get IP address
        ip = get_client_ip()

        # Get country information
        country_info = get_user_country()

        if country_info['success']:
            st.success("Location detected successfully!")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("IP Address", country_info['ip'])
                st.metric("Country", country_info['country'])
                st.metric("Country Code", country_info['country_code'])

            with col2:
                st.metric("City", country_info['city'])
                st.metric("Region", country_info['region'])

            # Show full data
            with st.expander("Full Response Data"):
                st.json(country_info)
        else:
            st.error(f"Failed to detect location: {country_info['error']}")
            st.info(f"IP Address: {country_info['ip']}")

st.markdown("---")
st.markdown("""
### How it works:
1. Detects your IP address from the connection
2. Uses ipapi.co API to lookup geolocation data
3. Returns country, city, and region information
4. Results are cached for 1 hour to reduce API calls

**Note:** Accuracy depends on your network setup. VPN/proxy users will see the VPN server location.
""")
