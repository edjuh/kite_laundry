# Oversight Marker: This file ensures configuration integrity for Kite Laundry Design Generator MVP.
# Last Verified: October 26, 2025, 4:58 PM CET by Grok 3 (xAI)
# Purpose: Stores secret key and SQLAlchemy settings. Verify against initial assignment (Start → Select → Configure → Output → Designs).
# Next Step: Ensure DB connection in app.py aligns with this URI.

SECRET_KEY = 'super_secret_key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///designs.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
