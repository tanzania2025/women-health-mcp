#!/usr/bin/env python3
"""
MCP Server for IP Geolocation.

Provides tools to get user's country and location based on IP address.
"""

import requests
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Geolocation")


def get_public_ip() -> Optional[str]:
    """
    Get the public IP address using external API.

    Returns:
        IP address string or None if failed
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip')
    except Exception:
        pass
    return None


@mcp.tool()
def get_country_from_ip(ip_address: Optional[str] = None) -> dict:
    """
    Get country and location information from an IP address.

    Args:
        ip_address: IP address to lookup (if None, auto-detects current public IP)

    Returns:
        Dictionary with location information including country, city, region, and country code
    """
    # Get IP if not provided
    if not ip_address:
        ip_address = get_public_ip()

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
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone', 'Unknown'),
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


@mcp.tool()
def get_user_location() -> dict:
    """
    Get the current user's location based on their public IP address.

    This is a convenience function that automatically detects the IP and returns location info.

    Returns:
        Dictionary with location information including country, city, region, and country code
    """
    return get_country_from_ip(None)


@mcp.tool()
def get_timezone_from_ip(ip_address: Optional[str] = None) -> dict:
    """
    Get timezone information for an IP address.

    Args:
        ip_address: IP address to lookup (if None, auto-detects current public IP)

    Returns:
        Dictionary with timezone information
    """
    location_data = get_country_from_ip(ip_address)

    if location_data['success']:
        return {
            'ip': location_data['ip'],
            'timezone': location_data.get('timezone', 'Unknown'),
            'country': location_data['country'],
            'success': True,
            'error': None
        }
    else:
        return {
            'ip': location_data['ip'],
            'timezone': 'Unknown',
            'country': 'Unknown',
            'success': False,
            'error': location_data.get('error', 'Failed to get timezone')
        }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
