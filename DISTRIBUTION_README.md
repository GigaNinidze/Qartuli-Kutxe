# ქართული კუთხე - Distribution Guide

## For Developers: Creating the Executable

To build a macOS executable that non-programmers can use:

### Prerequisites
- Python 3.8+ installed
- All dependencies installed: `pip install -r requirements.txt`

### Building the App
```bash
./build_executable.sh
```

This will create `dist/ქართული კუთხე.app` - a complete macOS application bundle.

### Distribution
1. Compress the app: `cd dist && zip -r 'ქართული კუთხე.zip' 'ქართული კუთხე.app'`
2. Share the zip file with users
3. Users extract and double-click the .app to run

## For End Users: Installing the App

### System Requirements
- macOS 10.15 (Catalina) or later
- No Python installation required

### Installation Steps
1. Download the `ქართული კუთხე.zip` file
2. Double-click to extract the app
3. Drag `ქართული კუთხე.app` to your Applications folder (optional)
4. Double-click the app to run

### First Launch
- macOS may show a security warning for unsigned apps
- Right-click the app → "Open" → "Open" to bypass this
- Or go to System Preferences → Security & Privacy → "Open Anyway"

### Features
- Generate advertisements with AI
- CSV file support for bulk operations
- Multiple tone options
- No technical knowledge required

## Troubleshooting

**App won't open**: Right-click → Open instead of double-clicking
**"App is damaged"**: Check if the download completed successfully
**Missing features**: Ensure you have the latest version

---
*Built with PyInstaller for easy distribution*
