#!/usr/bin/env python3
"""
WESTINGEN Demo Seed Script

This script creates demo data for the WESTINGEN application.
It sets up a company, an owner user, and a device with an API key.

WHY SEEDING INSTEAD OF SIGNUP?
- This is a job application demo, not a production system
- Seeding provides consistent demo credentials (owner@demo.com / demo1234)
- No need to implement user registration for a demo
- Makes it easy for recruiters to test the system

WHAT IT CREATES:
1. Company: "Demo Company" (the tenant)
2. User: owner@demo.com with password "demo1234" (role: owner)
3. Device: "robot-001" with a randomly generated API key

SAFE TO RERUN:
Uses INSERT ... ON CONFLICT to avoid errors if data already exists.
This means you can run it multiple times without breaking things.

SECURITY NOTE:
The password is intentionally simple ("demo1234") for demo purposes.
In production, users would set their own secure passwords.
"""

import sys
import os
# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db_connection
from app.auth import hash_password
import secrets

def seed_demo():
    """
    Create demo company, user, and device.
    
    When called: Manually by developer (python scripts/seed_demo.py)
    Returns: Nothing (prints credentials to console)
    
    This function is idempotent - safe to run multiple times.
    It uses ON CONFLICT clauses to handle existing data gracefully.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create demo company
        # ON CONFLICT (name) DO NOTHING: If company exists, skip creation
        # This makes the script safe to rerun
        cur.execute("""
            INSERT INTO companies (name)
            VALUES ('Demo Company')
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """)
        result = cur.fetchone()
        if result:
            # Company was just created
            company_id = result[0]
            print(f"✅ Created company: Demo Company (ID: {company_id})")
        else:
            # Company already exists - fetch its ID
            cur.execute("SELECT id FROM companies WHERE name = 'Demo Company'")
            company_id = cur.fetchone()[0]
            print(f"✅ Company already exists: Demo Company (ID: {company_id})")
        
        # Create owner user
        # Email and password are hardcoded for demo consistency
        email = 'owner@demo.com'
        password = 'demo1234'
        # Hash password before storing (never store plain passwords)
        password_hash = hash_password(password)
        
        # ON CONFLICT (email) DO UPDATE: If user exists, update password hash
        # This allows resetting the demo password by rerunning the script
        cur.execute("""
            INSERT INTO users (company_id, email, password_hash, role)
            VALUES (%s, %s, %s, 'owner')
            ON CONFLICT (email) DO UPDATE
            SET password_hash = EXCLUDED.password_hash
            RETURNING id
        """, (company_id, email, password_hash))
        
        result = cur.fetchone()
        if result:
            print(f"✅ Created/updated user: {email}")
        else:
            # Fallback: User exists but ON CONFLICT didn't return ID
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            print(f"✅ User already exists: {email}")
        
        # Create device with API key
        # Devices authenticate via X-DEVICE-KEY header, not user sessions
        device_name = 'robot-001'
        # Generate cryptographically secure random API key
        api_key = secrets.token_urlsafe(32)
        
        # Try to insert device
        # ON CONFLICT (api_key) won't work here because we generate new keys
        # So we check if device exists by name and company
        cur.execute("""
            INSERT INTO devices (company_id, name, api_key)
            VALUES (%s, %s, %s)
            ON CONFLICT (api_key) DO NOTHING
            RETURNING id, api_key
        """, (company_id, device_name, api_key))
        
        result = cur.fetchone()
        if result:
            # Device was created
            print(f"✅ Created device: {device_name}")
        else:
            # Device might exist with different key - fetch existing
            cur.execute("SELECT api_key FROM devices WHERE company_id = %s AND name = %s", 
                       (company_id, device_name))
            existing = cur.fetchone()
            if existing:
                # Use existing API key
                api_key = existing[0]
                print(f"✅ Device already exists: {device_name}")
            else:
                # Edge case: Try creating again with new key
                api_key = secrets.token_urlsafe(32)
                cur.execute("""
                    INSERT INTO devices (company_id, name, api_key)
                    VALUES (%s, %s, %s)
                    RETURNING api_key
                """, (company_id, device_name, api_key))
                api_key = cur.fetchone()[0]
                print(f"✅ Created device: {device_name}")
        
        # Commit all changes to database
        conn.commit()
        
        # Print credentials for user to copy
        print("\n" + "="*50)
        print("DEMO CREDENTIALS")
        print("="*50)
        print(f"Login URL: http://localhost:5001/login")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"\nDevice API Key: {api_key}")
        print("="*50)
        
    except Exception as e:
        # Rollback on error (don't save partial data)
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        # Always close database connection
        cur.close()
        conn.close()

if __name__ == '__main__':
    seed_demo()
