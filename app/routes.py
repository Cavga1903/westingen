"""
WESTINGEN Routes - Flask Blueprint for All Web Endpoints

This file defines all the URL routes (endpoints) for the WESTINGEN application.
It uses Flask Blueprints to organize routes into a single module.

B2B2C CONTEXT:
- B2B: Companies own devices and have users
- B2C: Users can only see data from their own company (tenant isolation)
- Devices authenticate via X-DEVICE-KEY header (not user sessions)

AUTHENTICATION PATTERNS:
1. User Authentication: Session-based (Flask sessions stored in cookies)
   - Used for: Dashboard, API stats, device management
   - Decorator: @login_required (checks session['user_id'])
   
2. Device Authentication: API Key in X-DEVICE-KEY header
   - Used for: POST /api/ingest (devices sending sensor data)
   - No session needed - device identity derived from API key

TENANT ISOLATION:
Every user query filters by company_id from session.
Devices are linked to companies, so device data is automatically scoped.
This ensures Company A users never see Company B data.
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from app.db import get_db_connection
from app.auth import login_required, owner_required, hash_password, check_password
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import secrets

# Flask Blueprint: Groups related routes together
# 'main' is the blueprint name, __name__ tells Flask where this blueprint is defined
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    """
    Main dashboard page - shows sensor data visualization.
    
    When called: User navigates to root URL (/) after login
    Returns: Rendered HTML template with company-specific data
    
    Tenant isolation: This route uses @login_required decorator which ensures
    session['company_id'] exists. The dashboard JavaScript then calls /api/latest
    and /api/stats, which filter by this company_id.
    
    Why server-rendered: This demo uses Jinja2 templates instead of React to
    keep the stack simple and demonstrate backend skills.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Fetch company name to display in navbar
    # session['company_id'] was set during login - this is how we know which company
    cur.execute("SELECT name FROM companies WHERE id = %s", (session['company_id'],))
    company = cur.fetchone()
    company_name = company['name'] if company else "Unknown"
    
    cur.close()
    conn.close()
    
    # Pass company_name and user_role to template so navbar can display them
    return render_template('dashboard.html', company_name=company_name, user_role=session.get('role'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page and authentication handler.
    
    When called: 
    - GET: User visits /login (shows login form)
    - POST: User submits login form (validates credentials)
    
    Returns: 
    - GET: Login form HTML
    - POST: Redirects to dashboard on success, shows error on failure
    
    Authentication flow:
    1. User enters email/password
    2. Lookup user in database by email
    3. Compare password hash (never store plain passwords)
    4. If valid: Store user_id, company_id, role in Flask session
    5. Session cookie is sent to browser, used for subsequent requests
    
    Why no @login_required: This route IS the login, so it must be public.
    """
    if request.method == 'POST':
        # Extract form data (HTML form submission)
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        # Database lookup: Find user by email
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, company_id, email, password_hash, role
            FROM users
            WHERE email = %s
        """, (email,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        # Password verification: Compare hashed password from DB with user input
        # check_password() hashes the input and compares with stored hash
        if not user or not check_password(user['password_hash'], password):
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        
        # Session creation: Store user identity in Flask session
        # Flask automatically creates a secure cookie containing this data
        # This cookie is sent with every subsequent request
        session['user_id'] = user['id']
        session['company_id'] = user['company_id']  # Critical for tenant isolation
        session['role'] = user['role']  # Used for authorization (owner vs operator)
        session['email'] = user['email']
        
        # Redirect to dashboard (user is now authenticated)
        return redirect(url_for('main.dashboard'))
    
    # GET request: Show login form
    return render_template('login.html')

@bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Logout handler - clears user session.
    
    When called: User clicks logout button (POST request from form)
    Returns: Redirects to login page
    
    Why POST: Logout should be a POST (not GET) to prevent accidental logout
    from browser prefetching or bookmarks.
    """
    # Clear all session data - user is now logged out
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/api/health')
def health():
    """
    Health check endpoint - public, no authentication required.
    
    When called: Monitoring systems, load balancers, or manual checks
    Returns: JSON with database connection status
    
    Why public: Health checks need to work even if auth is broken.
    Used for: System monitoring, deployment verification
    """
    try:
        # Simple database ping to verify connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@bp.route('/api/ingest', methods=['POST'])
def ingest():
    """
    Device sensor data ingestion endpoint.
    
    When called: Devices (or simulation scripts) POST sensor readings
    Returns: JSON with success status and created record ID
    
    DEVICE AUTHENTICATION (not user auth):
    - Devices use X-DEVICE-KEY header, not user sessions
    - API key is looked up in devices table
    - Device identity determines which company the data belongs to
    
    SECURITY: We do NOT trust client-provided device_id in the payload.
    Instead, we derive device identity from X-DEVICE-KEY header.
    This prevents a device from claiming to be another device.
    
    TENANT ISOLATION: company_id comes from the device record, not user input.
    This ensures data is automatically scoped to the correct company.
    """
    try:
        # Device authentication: Extract API key from custom header
        # X-DEVICE-KEY is a custom HTTP header (not standard, but clear for this demo)
        device_key = request.headers.get('X-DEVICE-KEY')
        if not device_key:
            return jsonify({"error": "Missing X-DEVICE-KEY header"}), 401
        
        # Device lookup: Find device by API key
        # This determines which company owns this device
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, company_id, name
            FROM devices
            WHERE api_key = %s
        """, (device_key,))
        
        device = cur.fetchone()
        if not device:
            # Invalid API key - device not found
            cur.close()
            conn.close()
            return jsonify({"error": "Invalid X-DEVICE-KEY"}), 401
        
        # Payload validation: Extract and validate JSON data
        data = request.get_json()
        if not data:
            cur.close()
            conn.close()
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Required fields check: Ensure all sensor metrics are present
        required_fields = ['temperature_c', 'accel_x', 'accel_y', 'accel_z', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            cur.close()
            conn.close()
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Type validation: Ensure numeric fields are actually numbers
        # This prevents SQL injection and data corruption
        numeric_fields = ['temperature_c', 'accel_x', 'accel_y', 'accel_z', 'latitude', 'longitude']
        invalid_fields = []
        for field in numeric_fields:
            if not isinstance(data[field], (int, float)):
                invalid_fields.append(field)
        
        if invalid_fields:
            cur.close()
            conn.close()
            return jsonify({"error": f"Non-numeric values in fields: {', '.join(invalid_fields)}"}), 400
        
        # Data insertion: Store sensor reading with tenant isolation
        # company_id comes from device record (not user input) - this is the security boundary
        # device_id_fk links to devices table, device_id (text) kept for backward compatibility
        cur.execute("""
            INSERT INTO sensor_readings 
            (company_id, device_id_fk, device_id, temperature_c, accel_x, accel_y, accel_z, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            device['company_id'],  # Tenant isolation: from device, not user input
            device['id'],           # Foreign key to devices table
            device['name'],         # Device name for display
            float(data['temperature_c']),
            float(data['accel_x']),
            float(data['accel_y']),
            float(data['accel_z']),
            float(data['latitude']),
            float(data['longitude'])
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "ok": True,
            "id": result['id'],
            "created_at": result['created_at'].isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/latest')
@login_required
def latest():
    """
    Get latest sensor readings - user-facing API endpoint.
    
    When called: Dashboard JavaScript calls this to refresh data table
    Returns: JSON array of sensor readings
    
    TENANT ISOLATION: 
    - Requires @login_required (ensures session['company_id'] exists)
    - WHERE clause filters by company_id from session
    - User can only see data from their own company
    
    Why this endpoint: Dashboard needs to display recent readings in a table.
    This is separate from /api/stats because it returns full records, not aggregates.
    """
    try:
        # Limit parameter: Prevent excessive data transfer
        limit = request.args.get('limit', 50, type=int)
        if limit > 1000:
            limit = 1000
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Tenant filtering: WHERE company_id = %s uses session['company_id']
        # This is the critical security pattern - every query scopes to user's company
        cur.execute("""
            SELECT id, created_at, device_id, temperature_c, 
                   accel_x, accel_y, accel_z, latitude, longitude
            FROM sensor_readings
            WHERE company_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (session['company_id'], limit))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format response: Convert database rows to JSON-serializable format
        readings = []
        for row in rows:
            readings.append({
                'id': row['id'],
                'created_at': row['created_at'].isoformat(),
                'device_id': row['device_id'],
                'temperature_c': float(row['temperature_c']),
                'accel_x': float(row['accel_x']),
                'accel_y': float(row['accel_y']),
                'accel_z': float(row['accel_z']),
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude'])
            })
        
        return jsonify({"readings": readings, "count": len(readings)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/stats')
@login_required
def stats():
    """
    Get aggregated statistics about sensor readings.
    
    When called: Dashboard JavaScript calls this to update KPI cards
    Returns: JSON with counts, averages, min/max values
    
    TENANT ISOLATION:
    - Requires @login_required (ensures session['company_id'] exists)
    - WHERE clause filters by company_id from session
    - Aggregations (COUNT, AVG, MIN, MAX) only include user's company data
    
    Why aggregated: Dashboard shows summary metrics (total records, avg temperature).
    This is more efficient than fetching all records and calculating in JavaScript.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Tenant-filtered aggregation: All statistics scoped to user's company
        # COUNT(*), AVG(), MIN(), MAX() only operate on rows matching company_id
        cur.execute("""
            SELECT 
                COUNT(*) as total_records,
                MIN(created_at) as first_reading,
                MAX(created_at) as last_reading,
                AVG(temperature_c) as avg_temperature,
                MIN(temperature_c) as min_temperature,
                MAX(temperature_c) as max_temperature,
                COUNT(DISTINCT device_id) as unique_devices
            FROM sensor_readings
            WHERE company_id = %s
        """, (session['company_id'],))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result['total_records'] == 0:
            return jsonify({
                "total_records": 0,
                "message": "No data available"
            }), 200
        
        return jsonify({
            "total_records": result['total_records'],
            "first_reading": result['first_reading'].isoformat() if result['first_reading'] else None,
            "last_reading": result['last_reading'].isoformat() if result['last_reading'] else None,
            "avg_temperature": float(result['avg_temperature']) if result['avg_temperature'] else None,
            "min_temperature": float(result['min_temperature']) if result['min_temperature'] else None,
            "max_temperature": float(result['max_temperature']) if result['max_temperature'] else None,
            "unique_devices": result['unique_devices']
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/devices', methods=['GET', 'POST'])
@owner_required
def admin_devices():
    """
    Device management page - create and list devices.
    
    When called: 
    - GET: Owner navigates to /admin/devices (shows device list and create form)
    - POST: Owner submits new device form (creates device with API key)
    
    Returns: Rendered HTML template with device list
    
    AUTHORIZATION:
    - @owner_required decorator ensures user role is 'owner'
    - Only owners can create devices (prevents unauthorized device creation)
    - Device list filtered by company_id (owner only sees their company's devices)
    
    API KEY GENERATION:
    - secrets.token_urlsafe(32) generates a cryptographically secure random key
    - This key is shown once to the user (they must save it)
    - Device uses this key in X-DEVICE-KEY header for authentication
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        # Device creation: Extract device name from form
        device_name = request.form.get('name', '').strip()
        if not device_name:
            flash('Device name is required', 'error')
        else:
            # Check if device name already exists for this company
            # Unique constraint ensures no duplicate names within same company
            cur.execute("""
                SELECT id FROM devices
                WHERE company_id = %s AND name = %s
            """, (session['company_id'], device_name))
            if cur.fetchone():
                flash(f'Device name "{device_name}" already exists. Please choose a different name.', 'error')
            else:
                # API key generation: Cryptographically secure random string
                # This key is what devices use in X-DEVICE-KEY header
                # Must be unique (enforced by database UNIQUE constraint)
                api_key = secrets.token_urlsafe(32)
                
                # Device insertion: Link device to company (tenant isolation)
                # session['company_id'] ensures device belongs to logged-in user's company
                cur.execute("""
                    INSERT INTO devices (company_id, name, api_key)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, api_key, created_at
                """, (session['company_id'], device_name, api_key))
                new_device = cur.fetchone()
                conn.commit()
                flash(f'Device created. API Key: {api_key}', 'success')
    
    # Device listing: Show all devices for current company
    # Tenant isolation: WHERE company_id = %s ensures owner only sees their devices
    cur.execute("""
        SELECT id, name, api_key, created_at
        FROM devices
        WHERE company_id = %s
        ORDER BY created_at DESC
    """, (session['company_id'],))
    
    devices = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('devices.html', devices=devices)
