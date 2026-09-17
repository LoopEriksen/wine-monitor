#!/usr/bin/env bash
# install.sh - Simple installation script for Wine Monitor on Raspberry Pi
# This script assumes a recent Debian/Ubuntu based system with python3.

set -e

echo "Updating package list..."
apt-get update -y

# Install python3 and pip if not present
echo "Installing python3 and pip..."
apt-get install -y python3 python3-venv python3-pip

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment and install requirements
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install systemd service
cat <<EOF > /etc/systemd/system/wine-monitor.service
[Unit]
Description=Wine Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:$PATH"
ExecStart=$(pwd)/venv/bin/python src/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling Wine Monitor service..."
systemctl enable --now wine-monitor.service

echo "Installation complete. Wine Monitor should be running now."
