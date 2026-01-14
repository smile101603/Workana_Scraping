#!/bin/bash
# Workana Scraper - Ubuntu VPS Setup Script
# Run this script to set up the scraper on a fresh Ubuntu server

set -e

echo "=========================================="
echo "Workana Scraper - Ubuntu Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please do not run as root. Run as a regular user with sudo privileges."
   exit 1
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "[1/6] Installing system dependencies..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    gnupg \
    software-properties-common \
    apt-transport-https \
    ca-certificates

echo ""
echo "[2/6] Installing Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt update
    sudo apt install -y google-chrome-stable
    echo "✅ Chrome installed: $(google-chrome --version)"
else
    echo "✅ Chrome already installed: $(google-chrome --version)"
fi

echo ""
echo "[3/6] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "[4/6] Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

echo ""
echo "[5/6] Setting up file permissions..."
chmod +x main.py
if [ -f ".env" ]; then
    chmod 600 .env
    echo "✅ .env file permissions set"
else
    echo "⚠️  .env file not found. Create it with your API keys."
fi

echo ""
echo "[6/6] Creating log directory..."
mkdir -p "$SCRIPT_DIR"
touch "$SCRIPT_DIR/scraper.log"
chmod 644 "$SCRIPT_DIR/scraper.log"
echo "✅ Log file ready"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Test the scraper:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Set up systemd service (optional):"
echo "   - Edit workana-scraper.service (replace YOUR_USERNAME)"
echo "   - sudo cp workana-scraper.service /etc/systemd/system/"
echo "   - sudo systemctl daemon-reload"
echo "   - sudo systemctl enable workana-scraper"
echo "   - sudo systemctl start workana-scraper"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
echo ""

