import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import Config

def get_db_connection():
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn

def init_db():
    """Initialize database connection and verify table exists."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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
