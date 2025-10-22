"""
Configuration settings for Women's Health MCP Server
"""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Security
    api_key: str = "demo-api-key-change-in-production"
    secret_key: str = "your-secret-key-here"
    
    # External API keys
    anthropic_api_key: Optional[str] = None
    
    # Database configuration
    database_url: str = "sqlite:///./womens_health_mcp.db"
    
    # MCP Configuration
    mcp_server_name: str = "women-health-mcp"
    mcp_version: str = "1.0.0"
    protocol_version: str = "2024-11-05"
    
    # Data source configurations
    enable_real_apis: bool = False  # Set to True for production
    
    # Research database APIs
    swan_api_url: Optional[str] = None
    swan_api_key: Optional[str] = None
    sart_api_url: Optional[str] = None
    sart_api_key: Optional[str] = None
    pubmed_api_key: Optional[str] = None
    
    # Patient data platforms
    clue_client_id: Optional[str] = None
    clue_client_secret: Optional[str] = None
    oura_client_id: Optional[str] = None
    oura_client_secret: Optional[str] = None
    
    # EHR integrations
    epic_client_id: Optional[str] = None
    epic_client_secret: Optional[str] = None
    cerner_client_id: Optional[str] = None
    cerner_client_secret: Optional[str] = None
    
    # Security and compliance
    encryption_key: Optional[str] = None
    enable_audit_logging: bool = True
    hipaa_compliance_mode: bool = True
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()