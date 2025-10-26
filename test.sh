#!/bin/bash
# Test script for Kite Laundry Design Generator MVP
echo "Creating virtual environment..."
python3 -m venv venv 2>> test_output.log
echo "Activating and testing..." >> test_output.log
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Installing dependencies..." >> test_output.log
    pip install -r requirements.txt >> test_output.log 2>&1
    echo "Running application..." >> test_output.log
    python app/app.py >> test_output.log 2>&1
    echo "Test completed. Check test_output.log for results." >> test_output.log
else
    echo "Virtual environment creation failed. Check test_output.log." >> test_output.log
fi
