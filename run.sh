#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"

echo "Setting up Kite Laundry Builder..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Virtual environment exists, activating..."
    source venv/bin/activate
fi

echo "Starting the application..."
python app.py

