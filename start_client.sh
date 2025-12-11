#!/bin/bash
# LiteDesk Client Launcher for Mac/Linux
# This script provides a user-friendly way to start the LiteDesk client

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "  LiteDesk Client Launcher"
echo "======================================"
echo ""

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
else
    PLATFORM="Unknown"
fi

echo "Platform: $PLATFORM"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"

# Check if dependencies are installed
echo ""
echo "Checking dependencies..."

DEPS_OK=true

if ! python3 -c "import mss" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Missing: mss${NC}"
    DEPS_OK=false
fi

if ! python3 -c "import PIL" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Missing: PIL/Pillow${NC}"
    DEPS_OK=false
fi

if ! python3 -c "import pynput" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Missing: pynput${NC}"
    DEPS_OK=false
fi

if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Missing: PyQt5${NC}"
    DEPS_OK=false
fi

if [ "$DEPS_OK" = true ]; then
    echo -e "${GREEN}✓ All dependencies are installed${NC}"
else
    echo ""
    echo "Installing missing dependencies..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Platform-specific instructions
echo ""
echo "======================================"
echo "  Platform-Specific Notes"
echo "======================================"

if [[ "$PLATFORM" == "macOS" ]]; then
    echo "macOS Requirements:"
    echo "1. Grant Accessibility permission:"
    echo "   System Preferences > Security & Privacy > Privacy > Accessibility"
    echo ""
elif [[ "$PLATFORM" == "Linux" ]]; then
    echo "Linux Requirements:"
    echo "1. X11 display server must be running"
    echo "2. DISPLAY environment variable must be set"
    echo "   Current DISPLAY: ${DISPLAY:-Not set}"
    echo ""
    
    if [ -z "$DISPLAY" ]; then
        echo -e "${RED}Warning: DISPLAY is not set${NC}"
        echo "The application may not work properly"
        echo ""
    fi
fi

# Start the client
echo "======================================"
echo "  Starting LiteDesk Client..."
echo "======================================"
echo ""

cd "$(dirname "$0")"
python3 client.py

# If client exits, show message
echo ""
echo "Client stopped."
