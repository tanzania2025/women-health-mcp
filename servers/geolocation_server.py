#!/usr/bin/env python3
"""
MCP Server for IP Geolocation.

Provides tools to get user's country and location based on IP address.
Uses ipapi.co for geolocation lookups with fallback to ipify.org for IP detection.
"""

import requests
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with proper name and description
mcp = FastMCP(
    "Geolocation",
    description="IP-based geolocation service that determines user's country, city, region, and timezone from IP addresses"
)


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


@mcp.tool(
    name="get_country_from_ip",
    description="Get detailed location information (country, city, region, timezone) for a given IP address or auto-detect current IP"
)
def get_country_from_ip(ip_address: Optional[str] = None) -> dict:
    """
    Get country and location information from an IP address.

    This tool retrieves comprehensive geolocation data including country name,
    country code (ISO 3166-1 alpha-2), city, region, timezone, and coordinates.

    Args:
        ip_address: IPv4 address to lookup (e.g., "8.8.8.8"). If None, automatically
                   detects and uses the current public IP address.

    Returns:
        Dictionary containing:
            - ip (str): The IP address that was looked up
            - country (str): Full country name (e.g., "United States")
            - country_code (str): Two-letter ISO country code (e.g., "US")
            - city (str): City name
            - region (str): State/province/region name
            - latitude (float): Latitude coordinate
            - longitude (float): Longitude coordinate
            - timezone (str): IANA timezone identifier (e.g., "America/New_York")
            - success (bool): Whether the lookup was successful
            - error (str|None): Error message if lookup failed, None otherwise

    Example:
        >>> get_country_from_ip("8.8.8.8")
        {
            "ip": "8.8.8.8",
            "country": "United States",
            "country_code": "US",
            "city": "Mountain View",
            "region": "California",
            "latitude": 37.4056,
            "longitude": -122.0775,
            "timezone": "America/Los_Angeles",
            "success": True,
            "error": None
        }
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


@mcp.tool(
    name="get_user_location",
    description="Automatically detect the current user's location by looking up their public IP address"
)
def get_user_location() -> dict:
    """
    Get the current user's location based on their public IP address.

    This is a convenience tool that automatically detects the user's public IP address
    and returns their location information. Useful when you need to know where the user
    is located without having their IP address.

    Returns:
        Dictionary containing the same fields as get_country_from_ip:
            - ip: The detected public IP address
            - country: Full country name
            - country_code: Two-letter ISO country code
            - city: City name
            - region: State/province/region name
            - latitude: Latitude coordinate
            - longitude: Longitude coordinate
            - timezone: IANA timezone identifier
            - success: Whether the lookup was successful
            - error: Error message if failed, None otherwise

    Example:
        >>> get_user_location()
        {
            "ip": "203.0.113.42",
            "country": "United Kingdom",
            "country_code": "GB",
            "city": "London",
            "region": "England",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "Europe/London",
            "success": True,
            "error": None
        }
    """
    return get_country_from_ip(None)


@mcp.tool(
    name="get_timezone_from_ip",
    description="Get timezone information for an IP address or auto-detect timezone from current IP"
)
def get_timezone_from_ip(ip_address: Optional[str] = None) -> dict:
    """
    Get timezone information for an IP address.

    This tool is useful when you only need timezone data without full location details.
    It returns the IANA timezone identifier for the given IP address.

    Args:
        ip_address: IPv4 address to lookup (e.g., "1.1.1.1"). If None, automatically
                   detects and uses the current public IP address.

    Returns:
        Dictionary containing:
            - ip (str): The IP address that was looked up
            - timezone (str): IANA timezone identifier (e.g., "America/New_York")
            - country (str): Country name for context
            - success (bool): Whether the lookup was successful
            - error (str|None): Error message if lookup failed, None otherwise

    Example:
        >>> get_timezone_from_ip("1.1.1.1")
        {
            "ip": "1.1.1.1",
            "timezone": "Australia/Sydney",
            "country": "Australia",
            "success": True,
            "error": None
        }
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
