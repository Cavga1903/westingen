"""
WESTINGEN Database Connection Module

This file handles all database connections for the application.
It provides a simple interface to PostgreSQL without using an ORM (Object-Relational Mapping).

WHY NO ORM (like SQLAlchemy)?
- This demo prioritizes clarity over abstraction
- Raw SQL makes tenant isolation explicit (you can see WHERE company_id = %s)
- Easier for junior developers to understand what's actually happening
- ORMs add complexity that doesn't serve this demo's purpose

DATABASE PATTERNS:
- get_db_connection(): Opens a new connection for each request
- RealDictCursor: Returns rows as dictionaries (row['column_name']) instead of tuples
- Always close connections: Prevents connection leaks

TENANT ISOLATION:
This module doesn't enforce tenant isolation - that happens in routes.py.
Every query in routes.py must include WHERE company_id = %s.
This file just provides the connection mechanism.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import Config

def get_db_connection():
    """
    Create and return a new PostgreSQL database connection.
    
    When called: Before executing any database query
    Returns: psycopg2 connection object
    
    Why per-request connections: Each HTTP request gets its own connection.
    This is simple and works for a demo. Production might use connection pooling.
    
    DATABASE_URL format: postgresql://user:password@host:port/database
    Read from environment variable or config file.
    """
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn

def init_db():
    """
    Initialize database connection and verify tables exist.
    
    When called: During Flask app startup (in app/__init__.py)
    Returns: Nothing (prints warnings if tables missing)
    
    Why this exists: Provides early warning if migrations haven't been run.
    Better to fail fast at startup than during first request.
    
    Note: This doesn't create tables - migrations do that.
    This just checks that tables exist.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if sensor_readings table exists
        # This is the core table, so if it's missing, migrations weren't run
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'sensor_readings'
            );
        """)
        table_exists = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        if not table_exists:
            print("WARNING: sensor_readings table does not exist. Run migration first.")
    except Exception as e:
        print(f"Database connection error: {e}")
