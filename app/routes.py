from flask import Blueprint, request, jsonify, render_template
from app.db import get_db_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/api/health')
def health():
    """Health check endpoint."""
    try:
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
    """Ingest sensor data."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['device_id', 'temperature_c', 'accel_x', 'accel_y', 'accel_z', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        numeric_fields = ['temperature_c', 'accel_x', 'accel_y', 'accel_z', 'latitude', 'longitude']
        invalid_fields = []
        for field in numeric_fields:
            if not isinstance(data[field], (int, float)):
                invalid_fields.append(field)
        
        if invalid_fields:
            return jsonify({"error": f"Non-numeric values in fields: {', '.join(invalid_fields)}"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_readings 
            (device_id, temperature_c, accel_x, accel_y, accel_z, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            data['device_id'],
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
            "status": "success",
            "id": result[0],
            "created_at": result[1].isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/latest')
def latest():
    """Get latest sensor readings."""
    try:
        limit = request.args.get('limit', 50, type=int)
        if limit > 1000:
            limit = 1000
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, created_at, device_id, temperature_c, 
                   accel_x, accel_y, accel_z, latitude, longitude
            FROM sensor_readings
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
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
def stats():
    """Get statistics about sensor readings."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
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
        """)
        
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
