#!/usr/bin/env python3
"""
Setup script for DoctHER - Women's Health AI Assistant
Prepares your environment to run the application
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")

def setup_env_file():
    """Setup .env file from example."""
    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_example.exists():
        print("⚠️  .env.example not found")
        print("   Creating minimal .env file...")
        env_file.write_text("# Add your Anthropic API key here\nANTHROPIC_API_KEY=your-api-key-here\n")
        print("✓ Created .env file")
        print("⚠️  You MUST add your ANTHROPIC_API_KEY to .env before running")
        return

    if env_file.exists():
        print("✓ .env file already exists")
        # Check if it has the API key
        content = env_file.read_text()
        if "your-api-key-here" in content or "ANTHROPIC_API_KEY=" not in content:
            print("⚠️  Make sure ANTHROPIC_API_KEY is set in .env file")
    else:
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from .env.example")
        print("⚠️  You MUST add your ANTHROPIC_API_KEY to .env before running")

def install_dependencies():
    """Install Python dependencies."""
    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    print("\n📦 Installing dependencies...")
    print("   This may take a few minutes...")

    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print(f"⚠️  Some dependencies may have failed:")
            if result.stderr:
                print(f"   {result.stderr[:200]}")
            print("\n   Try manually: pip install -r requirements.txt")
            return False
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Please run manually: pip install -r requirements.txt")
        return False

def verify_installation():
    """Verify key dependencies are installed."""
    print("\n🔍 Verifying installation...")

    required_packages = [
        ("streamlit", "Streamlit"),
        ("anthropic", "Anthropic SDK"),
        ("fastmcp", "FastMCP"),
        ("httpx", "HTTPX"),
        ("mcp", "MCP SDK")
    ]

    all_good = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ❌ {name} - not installed")
            all_good = False

    return all_good

def main():
    """Main setup function."""
    print("🚀 DoctHER Setup")
    print("="*50)
    print("Setting up Women's Health AI Assistant...")
    print()

    # Check Python version
    check_python_version()

    # Setup environment file
    setup_env_file()

    # Install dependencies
    deps_ok = install_dependencies()

    # Verify installation
    if deps_ok:
        verify_installation()

    print("\n" + "="*50)
    print("✅ Setup complete!")
    print("\n📝 Next steps:")
    print("   1. Edit .env file and add your ANTHROPIC_API_KEY")
    print("      Get your key from: https://console.anthropic.com/")
    print()
    print("   2. Start DoctHER:")
    print("      → streamlit run demos/doct_her_stdio.py")
    print()
    print("   The MCP server will start automatically!")
    print("="*50)

if __name__ == "__main__":
    main()