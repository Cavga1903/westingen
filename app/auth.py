"""
WESTINGEN Authentication Helpers

This file provides authentication and authorization decorators and utilities.
It handles user authentication (session-based) and password hashing.

AUTHENTICATION vs AUTHORIZATION:
- Authentication: "Who are you?" (login_required checks if user is logged in)
- Authorization: "What can you do?" (owner_required checks if user has owner role)

DECORATORS:
Python decorators (@login_required) wrap functions to add behavior.
They check authentication before allowing the function to run.
If not authenticated, they redirect to login or return 401 error.

PASSWORD SECURITY:
Never store plain passwords. Always hash them using werkzeug.security.
Hashing is one-way - you can't recover the original password.
To verify login, hash the input and compare with stored hash.
"""

from functools import wraps
from flask import session, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(f):
    """
    Decorator to require user login for a route.
    
    Usage: @login_required above any route function
    
    How it works:
    1. Checks if session['user_id'] exists (user is logged in)
    2. If not logged in:
       - API routes: Return 401 JSON error
       - Web routes: Redirect to login page
    3. If logged in: Allow function to run normally
    
    When to use: Any route that should only be accessible to logged-in users.
    Examples: Dashboard, API stats, device management.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Session check: Flask session is stored in encrypted cookie
        # session['user_id'] was set during login (in routes.py)
        if 'user_id' not in session:
            # Different response for API vs web routes
            if request.path.startswith('/api/'):
                # API endpoints return JSON errors
                from flask import jsonify
                return jsonify({"error": "Authentication required"}), 401
            # Web pages redirect to login
            return redirect(url_for('main.login'))
        # User is authenticated - proceed with original function
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    """
    Decorator to require owner role for a route.
    
    Usage: @owner_required above any route function
    
    How it works:
    1. First checks login (via session['user_id'])
    2. Then checks role (session['role'] must be 'owner')
    3. If not owner: Return 403 Forbidden
    
    When to use: Routes that only owners should access.
    Example: Device management (creating devices).
    
    ROLE HIERARCHY:
    - owner: Can create devices, full access
    - manager: (future: can view but not create)
    - operator: (future: read-only access)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check: Is user logged in?
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                from flask import jsonify
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('main.login'))
        
        # Second check: Is user an owner?
        # session['role'] was set during login
        if session.get('role') != 'owner':
            from flask import jsonify, abort
            if request.path.startswith('/api/'):
                return jsonify({"error": "Owner role required"}), 403
            # Web routes: HTTP 403 Forbidden
            abort(403)
        
        # User is authenticated AND is owner - proceed
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """
    Hash a plain text password for storage.
    
    When called: During user creation (seed script) or password reset
    Returns: Hashed password string (safe to store in database)
    
    Why hash: Never store plain passwords. If database is compromised,
    attackers can't recover original passwords (hashing is one-way).
    
    Algorithm: werkzeug uses PBKDF2 with salt (cryptographically secure).
    Method 'pbkdf2:sha256' is used for compatibility with Python 3.9.
    """
    return generate_password_hash(password, method='pbkdf2:sha256')

def check_password(password_hash, password):
    """
    Verify a password against its hash.
    
    When called: During login (compare user input with stored hash)
    Returns: True if password matches, False otherwise
    
    How it works:
    1. Takes stored hash from database
    2. Hashes the user's input password
    3. Compares the two hashes
    4. Returns True only if they match
    
    Security: Even if you know the hash, you can't reverse it to get the password.
    You can only verify by hashing a guess and comparing.
    """
    return check_password_hash(password_hash, password)
