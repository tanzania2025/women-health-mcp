"""
Geolocation service to determine user's country from IP address.

Uses ipapi.co API for IP geolocation.
"""

import requests
import streamlit as st
from typing import Dict, Optional


def get_client_ip() -> Optional[str]:
    """
    Get the client's IP address from Streamlit context.

    Returns:
        IP address string or None if not available
    """
    try:
        # Try to get from Streamlit session info
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx:
            session_id = ctx.session_id
            session_info = st.runtime.get_instance()._session_mgr.get_session_info(session_id)
            if session_info and hasattr(session_info, 'ws') and session_info.ws:
                # Get IP from WebSocket connection
                client_ip = session_info.ws.request.remote_ip
                return client_ip
    except Exception:
        pass

    # Fallback: use external service to get public IP
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip')
    except Exception:
        pass

    return None


def get_country_from_ip(ip_address: Optional[str] = None) -> Dict[str, str]:
    """
    Get country information from IP address.

    Args:
        ip_address: IP address to lookup (if None, auto-detects)

    Returns:
        Dictionary with country information:
        {
            'ip': str,
            'country': str,
            'country_code': str,
            'city': str,
            'region': str,
            'success': bool,
            'error': Optional[str]
        }
    """
    # Get IP if not provided
    if not ip_address:
        ip_address = get_client_ip()

    if not ip_address:
        return {
            'ip': None,
            'country': 'Unknown',
            'country_code': 'XX',
            'city': 'Unknown',
            'region': 'Unknown',
            'success': False,
            'error': 'Could not determine IP address'
        }

    try:
        # Use ipapi.co for geolocation (free tier: 1000 requests/day)
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Check if we got an error response
            if 'error' in data:
                return {
                    'ip': ip_address,
                    'country': 'Unknown',
                    'country_code': 'XX',
                    'city': 'Unknown',
                    'region': 'Unknown',
                    'success': False,
                    'error': data.get('reason', 'Unknown error')
                }

            return {
                'ip': ip_address,
                'country': data.get('country_name', 'Unknown'),
                'country_code': data.get('country_code', 'XX'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'success': True,
                'error': None
            }
        else:
            return {
                'ip': ip_address,
                'country': 'Unknown',
                'country_code': 'XX',
                'city': 'Unknown',
                'region': 'Unknown',
                'success': False,
                'error': f'API returned status code {response.status_code}'
            }

    except requests.RequestException as e:
        return {
            'ip': ip_address,
            'country': 'Unknown',
            'country_code': 'XX',
            'city': 'Unknown',
            'region': 'Unknown',
            'success': False,
            'error': str(e)
        }


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_country_info(ip_address: str) -> Dict[str, str]:
    """
    Get country information with caching.

    Args:
        ip_address: IP address to lookup

    Returns:
        Dictionary with country information
    """
    return get_country_from_ip(ip_address)


def get_user_country() -> Dict[str, str]:
    """
    Convenience function to get current user's country information.

    Returns:
        Dictionary with country information
    """
    ip = get_client_ip()
    if ip:
        return get_cached_country_info(ip)
    else:
        return get_country_from_ip(None)
