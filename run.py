#!/usr/bin/env python3
"""
Simple launcher for Kite Laundry Builder
"""

import os
import sys
from Core.applications.app import app

if __name__ == "__main__":
    # Add Core to path to ensure imports work
    sys.path.append(os.path.join(os.path.dirname(__file__), 'Core'))
    
    # Run the application
    app.run(debug=True)

