# Oversight Marker: Last Verified: October 26, 2025, 6:49 PM CET by Grok 3 (xAI)
# Purpose: Initializes Flask app for Kite Laundry Design Generator MVP.
# Next Step: Add main routes in Step 5.

from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
