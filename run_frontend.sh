#!/bin/bash
# Frontend launcher script for DoctHER

echo "🌐 Starting DoctHER Frontend..."

# Get the directory of this script (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "📁 Project root: $SCRIPT_DIR"
echo "📁 Frontend directory: $FRONTEND_DIR"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Check if app.py exists
if [ ! -f "$FRONTEND_DIR/app.py" ]; then
    echo "❌ app.py not found in frontend directory"
    exit 1
fi

# Set Python path to include project root
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Change to frontend directory and run streamlit
cd "$FRONTEND_DIR"

echo "🚀 Starting Streamlit..."
echo "   PYTHONPATH: $PYTHONPATH"
echo "   Current dir: $(pwd)"

# Run streamlit
streamlit run app.py

echo "👋 Frontend stopped"