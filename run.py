#!/usr/bin/env python3
"""
WESTINGEN Flask Application Entry Point

This is the main entry point for running the WESTINGEN application.
It creates the Flask app and starts the development server.

HOW TO RUN:
    python run.py

This starts a development server on http://localhost:5001
(Port 5001 instead of 5000 because macOS reserves 5000 for AirPlay)

DEVELOPMENT vs PRODUCTION:
- debug=True: Shows detailed error pages (only for development)
- host='0.0.0.0': Allows connections from any IP (not just localhost)
- For production, use a proper WSGI server (gunicorn, uwsgi)
"""

from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This sets DATABASE_URL, SECRET_KEY, etc. before app creation
load_dotenv()

# Create Flask application instance
# This calls create_app() from app/__init__.py
app = create_app()

# Run development server
# This only runs if script is executed directly (not imported)
if __name__ == '__main__':
    # Development server settings
    # debug=True: Auto-reload on code changes, detailed error pages
    # host='0.0.0.0': Listen on all network interfaces
    # port=5001: Use port 5001 (5000 is reserved on macOS)
    app.run(debug=True, host='0.0.0.0', port=5001)
