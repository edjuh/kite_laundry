#!/bin/bash
# Test script for Kite Laundry Design Generator MVP
echo "Creating virtual environment..."
[ ! -d "venv" ] && python3 -m venv venv
echo "Activating and testing..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    pip install -r requirements.txt > test_output.log 2>&1
    python app/app.py >> test_output.log 2>&1
    echo "Test completed. Check test_output.log for results."
else
    echo "Virtual environment not found. Create with 'python3 -m venv venv'." > test_output.log
fi
