# Creating Executable for ქართული კუთხე

The PyInstaller approach is experiencing recursion issues with your current environment. Here are several alternative approaches to create an executable for non-programmers:

## Option 1: Use a Different Environment (Recommended)

### Step 1: Create a Clean Virtual Environment
```bash
# Create a new virtual environment
python3 -m venv venv_build
source venv_build/bin/activate

# Install only essential dependencies
pip install PySide6==6.6.0 openai==1.2.3 pandas==2.1.0 python-dotenv==1.0.0
pip install PyInstaller==5.13.2  # Use older, more stable version
```

### Step 2: Simple Build Command
```bash
pyinstaller --onefile --windowed --name="Georgian_Corner" \
  --icon="assets/icon.png" \
  --add-data="assets:assets" \
  --add-data="prompts:prompts" \
  --add-data="config:config" \
  main.py
```

## Option 2: Using py2app (macOS Native)

### Install py2app
```bash
pip install py2app
```

### Create setup.py
```python
from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('assets', ['assets/icon.png']),
    ('prompts', ['prompts/base_prompts.py', 'prompts/tone_prompts.py']),
    ('config', ['config/settings.py', 'config/api_keys.py'])
]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/icon.png',
    'plist': {
        'CFBundleName': 'ქართული კუთხე',
        'CFBundleDisplayName': 'ქართული კუთხე',
        'CFBundleIdentifier': 'com.georgiankorner.app',
        'CFBundleVersion': '1.0.0',
        'LSMinimumSystemVersion': '10.15.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Build with py2app
```bash
python setup.py py2app
```

## Option 3: Docker + Executable

Create a containerized build environment to avoid dependency conflicts.

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install PyInstaller==5.13.2

COPY . .
RUN pyinstaller --onefile --name="Georgian_Corner" main.py

CMD ["./dist/Georgian_Corner"]
```

## Option 4: GitHub Actions (Automated)

Create `.github/workflows/build.yml` to automatically build executables:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install PyInstaller==5.13.2
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed --name="Georgian_Corner" \
          --icon="assets/icon.png" \
          --add-data="assets:assets" \
          --add-data="prompts:prompts" \
          --add-data="config:config" \
          main.py
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: georgian-corner-macos
        path: dist/Georgian_Corner
```

## Option 5: Manual Distribution (Simplest)

### Create a simple launcher script:
```bash
#!/bin/bash
# Save as: run_app.sh

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Please install Python 3.8+ from python.org"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "pip is required. Please install pip"
    exit 1
fi

# Install dependencies if needed
pip3 install --user PySide6 openai pandas python-dotenv

# Run the application
python3 main.py
```

### Make it executable:
```bash
chmod +x run_app.sh
```

### Create a simple installer package:
```bash
# Create installer directory
mkdir -p "Georgian_Corner_Installer"
cp -r * "Georgian_Corner_Installer/"
cd "Georgian_Corner_Installer"

# Create README for users
cat > README_USERS.txt << EOF
# ქართული კუთხე - Installation Guide

## For macOS Users:

1. Double-click 'run_app.sh' to start the application
2. If prompted, allow the script to install Python dependencies
3. The app will start automatically

## First Time Setup:
- You'll need to enter your OpenAI API key when prompted
- The app will remember your settings for future use

## System Requirements:
- macOS 10.15 or later
- Internet connection (for AI features)

## Troubleshooting:
- If the script doesn't run, right-click → "Open With" → "Terminal"
- If you get permission errors, open Terminal and run: chmod +x run_app.sh

For support, contact: [your-email@example.com]
EOF

# Create zip for distribution
cd ..
zip -r "Georgian_Corner_v1.0_macOS.zip" "Georgian_Corner_Installer/"
```

## Recommendation

**Start with Option 5** (Manual Distribution) as it's the most reliable and doesn't require complex build processes. Users can easily run your app, and you avoid the current PyInstaller issues.

For a more polished solution later, try **Option 1** with a clean virtual environment, or **Option 2** with py2app for a native macOS app bundle.

## Current Issue Analysis

The recursion error you're experiencing is likely due to:
1. Complex dependency tree in your current environment
2. Conflicting package versions
3. PyInstaller trying to analyze too many nested imports

Using a clean environment or alternative tools should resolve this.
