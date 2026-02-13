# MIST Visual Interface - Build Instructions

## Overview
This document provides instructions for building and deploying the MIST Visual Interface application.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip package manager
- Windows, macOS, or Linux operating system

### Development Tools
- Git (for cloning the repository)
- Terminal/command prompt access
- Administrator privileges (if installing system-wide)

## Installation

### 1. Clone the Repository
```bash
cd C:\Users\nator\clawd\personal-ide
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install dependencies individually:
```bash
pip install Pillow pygame aiohttp websockets
```

### 3. Verify Installation
```bash
python -c "import tkinter, pygame, PIL; print('Dependencies installed successfully')"
```

## Running the Application

### Development Mode
```bash
python LAUNCH_VISUAL.py
```

### Alternative Launch Method
```bash
python VISUAL_INTERFACE.py
```

## Building for Distribution

### Option 1: Using PyInstaller (Recommended)
1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build executable:
```bash
pyinstaller --onefile --windowed --name "MIST_Visual_Interface" --icon=icon.ico LAUNCH_VISUAL.py
```

Note: Create an icon.ico file for your application icon, or omit the --icon parameter.

3. Find the executable in the `dist/` folder

### Option 2: Create a Virtual Environment
1. Create virtual environment:
```bash
python -m venv mist_env
```

2. Activate virtual environment:
- On Windows:
```bash
mist_env\Scripts\activate
```
- On macOS/Linux:
```bash
source mist_env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run application:
```bash
python LAUNCH_VISUAL.py
```

## Application Structure

### Core Components
- `LAUNCH_VISUAL.py` - Main entry point
- `VISUAL_INTERFACE.py` - Main GUI application
- `integration/CORE_HUB.py` - Core communication hub
- `visualization/VISUAL_COMPANION.py` - Visual companion logic
- `voice/VOICE_SYNTHESIZER.py` - Voice synthesis functionality
- `memory/MEMORY_NODES.py` - Memory management
- `integration/AI_CONNECTOR.py` - AI integration

### Supporting Files
- `sprites/` - Sprite images and animations
- `production_sprites/` - Production-ready sprites
- Various configuration and documentation files

## Configuration

### Environment Variables
The application may use environment variables for API keys or configuration:

```bash
# Example environment variables
export MIST_AI_PROVIDER="ollama"  # or "openai", "anthropic", etc.
export MIST_MODEL_NAME="llama3.3"  # or your preferred model
export MIST_VOICE_ENABLED="true"  # enable/disable voice features
```

## Troubleshooting

### Common Issues

#### 1. Module Not Found Errors
- Ensure you're running Python from the correct directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

#### 2. Pygame/Tkinter Issues
- Some Python installations don't include tkinter by default
- On Ubuntu/Debian: `sudo apt-get install python3-tk`
- On CentOS/RHEL: `sudo yum install tkinter`

#### 3. Audio Issues
- Ensure your system has audio capabilities
- Check that no other applications are using exclusive audio access

#### 4. Display Issues
- Ensure your display drivers are up to date
- Try running with administrator privileges if on Windows

### Performance Tips
- Close unnecessary applications to free up memory
- Reduce visual effects if experiencing slow performance
- Ensure sufficient RAM (4GB+ recommended)

## Deployment

### For End Users
1. Distribute the executable created with PyInstaller
2. Ensure target systems meet minimum requirements
3. Provide clear installation instructions

### For Development
1. Use the source code directly
2. Maintain a virtual environment for clean dependencies
3. Use version control for tracking changes

## Updating

### To Update the Application
1. Pull latest changes from repository
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Test functionality

## Security Considerations

- Keep dependencies updated for security patches
- Validate all user inputs
- Store sensitive information (API keys) securely
- Run with minimal required privileges

## Support

For support, please check:
- Documentation in the docs/ directory
- Issue tracker (if using version control)
- Contact information in the README.md

---

Built with ❤️ for the MIST ecosystem