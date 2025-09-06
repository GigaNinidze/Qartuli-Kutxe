#!/bin/bash
# Georgian Corner Launcher

echo "🚀 Starting ქართული კუთხე..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8+ from python.org"
    open "https://www.python.org/downloads/"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install --user --quiet PySide6>=6.6.0 openai>=1.2.3 pandas>=2.1.0 python-dotenv>=1.0.0

# Run the application
echo "✅ Launching application..."
python3 main.py
