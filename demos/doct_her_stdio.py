"""
Redirect file for backward compatibility with Streamlit Cloud deployment.
The actual application is now located at app/doct_her_stdio.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the actual app from the new location
from app.doct_her_stdio import *

# This ensures all the app code runs
if __name__ == "__main__":
    pass  # The import above executes the streamlit app
