#!/bin/bash

# Build script for creating macOS executable
# Multiple approaches to handle different environments

set -e

echo "🏗️  Building ქართული კუთხე executable for macOS..."

# Function to try PyInstaller build
try_pyinstaller() {
    echo "📦 Trying PyInstaller approach..."
    
    # Clean previous builds
    echo "🧹 Cleaning previous builds..."
    rm -rf build/ dist/ *.spec
    
    # Try simple PyInstaller command first
    echo "🔨 Building with simple command..."
    pyinstaller --onefile --windowed \
        --name="Georgian_Corner" \
        --icon="assets/icon.png" \
        --add-data="assets:assets" \
        --add-data="prompts:prompts" \
        --add-data="config:config" \
        main.py
    
    if [[ -f "dist/Georgian_Corner" ]]; then
        echo "✅ PyInstaller build successful!"
        echo "📱 Executable created at: dist/Georgian_Corner"
        return 0
    else
        echo "❌ PyInstaller build failed"
        return 1
    fi
}

# Function to create manual distribution
create_manual_distribution() {
    echo "📦 Creating manual distribution package..."
    
    # Create distribution directory
    DIST_DIR="Georgian_Corner_v1.0_macOS"
    rm -rf "$DIST_DIR" "$DIST_DIR.zip"
    mkdir -p "$DIST_DIR"
    
    # Copy all necessary files
    cp -r assets config core gui prompts utils main.py requirements.txt "$DIST_DIR/"
    
    # Create launcher script
    cat > "$DIST_DIR/run_app.sh" << 'EOF'
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
EOF

    # Make launcher executable
    chmod +x "$DIST_DIR/run_app.sh"
    
    # Create user README
    cat > "$DIST_DIR/README_FOR_USERS.txt" << EOF
# ქართული კუთხე - Georgian Corner

## Quick Start (macOS):
1. Double-click 'run_app.sh' to start the application
2. If prompted, allow installation of Python dependencies
3. Enter your OpenAI API key when requested

## If the app doesn't start:
1. Right-click 'run_app.sh' → "Open With" → "Terminal"
2. Or open Terminal, navigate to this folder, and run: ./run_app.sh

## System Requirements:
- macOS 10.15 or later
- Internet connection
- Python 3.8+ (will be installed if needed)

## First Time Setup:
- You'll be asked for your OpenAI API key
- The app saves your preferences automatically

## Troubleshooting:
- Permission errors: Run 'chmod +x run_app.sh' in Terminal
- Python not found: Install from python.org
- Dependencies fail: Try 'pip3 install --upgrade pip' first

Enjoy creating advertisements with AI! 🎨
EOF
    
    # Create zip package
    zip -r "$DIST_DIR.zip" "$DIST_DIR/"
    
    echo "✅ Manual distribution created!"
    echo "📱 Package created: $DIST_DIR.zip"
    echo "📁 Folder created: $DIST_DIR/"
    
    return 0
}

# Main execution
echo "🎯 Attempting multiple build approaches..."

# Try PyInstaller first (if it works, great!)
if try_pyinstaller; then
    echo ""
    echo "🚀 PyInstaller build successful! You can distribute:"
    echo "   📱 Single executable: dist/Georgian_Corner"
    echo ""
    echo "💡 To create app bundle, try: pip install py2app"
    
    # Also create manual distribution as backup
    echo ""
    echo "🔄 Also creating manual distribution as backup..."
    create_manual_distribution
else
    echo ""
    echo "⚠️  PyInstaller failed, creating manual distribution..."
    create_manual_distribution
fi

echo ""
echo "🎉 Build process complete!"
echo ""
echo "📋 Distribution options created:"
echo "   1. Manual distribution (most reliable): Georgian_Corner_v1.0_macOS.zip"
if [[ -f "dist/Georgian_Corner" ]]; then
    echo "   2. Single executable: dist/Georgian_Corner"
fi
echo ""
echo "📖 See BUILD_EXECUTABLE_GUIDE.md for more options and troubleshooting"

# Open the current directory to show results
open .
