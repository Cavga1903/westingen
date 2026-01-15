"""
WESTINGEN Configuration Module

This file centralizes all configuration settings for the application.
It reads from environment variables with sensible defaults.

WHY SEPARATE CONFIG FILE?
- Keeps sensitive data (database URLs, secrets) out of code
- Easy to change settings without modifying application code
- Environment variables allow different configs for dev/staging/prod

CONFIGURATION VALUES:
- DATABASE_URL: PostgreSQL connection string
- SECRET_KEY: Flask session encryption key (must be secret in production)

ENVIRONMENT VARIABLES:
Set these in .env file (loaded by python-dotenv) or system environment.
Never commit .env to git (it's in .gitignore).
"""

import os

class Config:
    """
    Application configuration class.
    
    All settings are class attributes (accessed as Config.DATABASE_URL).
    Flask automatically loads this via app.config.from_object().
    """
    
    # Database connection string
    # Format: postgresql://user:password@host:port/database
    # Default assumes local PostgreSQL with database named 'westingen'
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/westingen')
    
    # Flask session encryption key
    # Used to sign session cookies so users can't tamper with them
    # In production, this MUST be a strong random secret
    # Default is insecure - only for local development
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
