#!/bin/bash
# LiteDesk Quick Start Script

echo "==========================================="
echo "  LiteDesk - Simple P2P Remote Desktop"
echo "==========================================="
echo ""

# Check Python version
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Select mode:"
echo "1) Start Server (share your desktop)"
echo "2) Start Client (connect to remote desktop)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Starting LiteDesk Server..."
        echo "After starting, share your IP address with the client."
        echo ""
        python3 server.py
        ;;
    2)
        echo ""
        echo "Starting LiteDesk Client..."
        echo "You will need the server's IP address to connect."
        echo ""
        python3 client.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
