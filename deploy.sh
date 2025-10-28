#!/bin/bash
# Deploy script for Kite Laundry Design Generator MVP
echo "Creating virtual environment..." >> deploy.log
python3 -m venv venv 2>> deploy.log
echo "Activating and testing..." >> deploy.log
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Installing dependencies..." >> deploy.log
    pip install -r requirements.txt >> deploy.log 2>&1 || { echo "Dependency installation failed. Check deploy.log." >> deploy.log; exit 1; }
    echo "Running application..." >> deploy.log
    python app/app.py >> deploy.log 2>&1 || { echo "Application failed to start. Check deploy.log." >> deploy.log; exit 1; }
    echo "Test completed. Check deploy.log for results." >> deploy.log
else
    echo "Virtual environment creation failed. Check deploy.log." >> deploy.log
    exit 1
fi
git add app/ deploy.sh deploy.log AI/
git commit -m "Deployed and finalized Kite Laundry Design Generator MVP with fixed dependencies - Take 8 - October 27, 2025"
git push origin main
