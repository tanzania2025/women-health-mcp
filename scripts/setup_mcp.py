#!/usr/bin/env python3
"""
Quick setup script for Women's Health MCP Server
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories."""
    dirs = [
        "data/samples",
        "data/schemas", 
        "data/exports",
        "data/uploads",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def setup_env_file():
    """Setup .env file from example."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from example")
        print("⚠️  Update .env file with your API keys before running server")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("❌ .env.example not found")

def install_dependencies():
    """Install Python dependencies."""
    try:
        import subprocess
        print("Installing dependencies...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
        else:
            print(f"⚠️  Some dependencies may have failed to install: {result.stderr}")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Please run manually: pip install -r requirements.txt")

def main():
    """Main setup function."""
    print("🔧 Setting up Women's Health MCP Server...")
    print("="*50)
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_env_file()
    
    # Install dependencies
    install_dependencies()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your API keys")
    print("2. Run DoctHER: streamlit run demos/doct_her_stdio.py")
    print("\nFor Anthropic integration:")
    print("- Add ANTHROPIC_API_KEY to .env file")

if __name__ == "__main__":
    main()