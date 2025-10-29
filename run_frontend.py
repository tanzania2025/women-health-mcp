#!/usr/bin/env python3
"""
Frontend launcher script - runs app.py from project root
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the directory of this script (project root)
project_root = Path(__file__).parent

print("🌐 Starting DoctHER Frontend...")
print(f"🔧 Project root: {project_root}")

# Check if required files exist
if not (project_root / "app.py").exists():
    print(f"❌ app.py not found in: {project_root}")
    sys.exit(1)

if not (project_root / "mcp_client.py").exists():
    print(f"❌ mcp_client.py not found in: {project_root}")
    sys.exit(1)

# Set up environment
current_pythonpath = os.environ.get('PYTHONPATH', '')
new_pythonpath = f"{project_root}:{current_pythonpath}" if current_pythonpath else str(project_root)
os.environ['PYTHONPATH'] = new_pythonpath

print(f"🔧 PYTHONPATH: {new_pythonpath}")

try:
    # Run streamlit from project root
    os.chdir(project_root)
    print(f"🚀 Running: streamlit run app.py")
    print(f"📍 Working directory: {Path.cwd()}")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
except KeyboardInterrupt:
    print("\n👋 Frontend stopped")
except Exception as e:
    print(f"❌ Error running frontend: {e}")
    print("\n🔧 Manual run options:")
    print(f"  Option 1: cd {project_root} && streamlit run app.py")
    print(f"  Option 2: python run_frontend.py")
    print(f"  Option 3: streamlit run app.py")