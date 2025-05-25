#!/bin/bash

REPO_URL="https://github.com/taranenkom/AWS_University"
PROJECT_DIR="AWS_University"

echo "[*] Cloning repository..."
git clone "$REPO_URL"
cd "$PROJECT_DIR" || { echo "[!] Failed to enter repo directory."; exit 1; }

echo "[*] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[*] Installing dependencies..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "[*] Found requirements.txt. Installing from it..."
    pip install -r requirements.txt
else
    echo "[!] requirements.txt not found. Installing default packages..."
    pip install boto3 pandas matplotlib requests
fi

echo "[+] Environment setup complete!"
