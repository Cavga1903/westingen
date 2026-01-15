"""
WESTINGEN Flask Application Factory

This file creates and configures the Flask application instance.
It uses the "application factory" pattern - a function that returns an app.

WHY APPLICATION FACTORY?
- Allows creating multiple app instances (useful for testing)
- Configuration happens in one place
- Blueprints are registered here (routes organized in separate file)

APPLICATION SETUP FLOW:
1. create_app() is called (from run.py)
2. Flask app instance created
3. Configuration loaded from Config class
4. Database initialized (checks tables exist)
5. Blueprint registered (routes from routes.py)
6. App returned and ready to run
"""

from flask import Flask
from app.db import init_db

def create_app():
    """
    Create and configure Flask application instance.
    
    When called: From run.py when starting the server
    Returns: Configured Flask app ready to handle requests
    
    This is the entry point for the entire application.
    All configuration, database setup, and route registration happens here.
    """
    # Create Flask app instance
    # __name__ tells Flask where to find templates and static files
    app = Flask(__name__)
    
    # Load configuration from Config class
    # This sets DATABASE_URL, SECRET_KEY, etc.
    app.config.from_object('app.config.Config')
    
    # Initialize database connection and verify tables exist
    # This prints warnings if migrations haven't been run
    init_db()
    
    # Register Blueprint: Import routes from routes.py
    # This connects all the @bp.route() decorators to the app
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Return configured app
    return app
