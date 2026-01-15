#!/usr/bin/env python3
"""
WESTINGEN Fake Data Generator

This script simulates a real device sending sensor data to the WESTINGEN API.
It generates realistic sensor readings and POSTs them to /api/ingest.

DEVICE SIMULATION:
- Real devices would be physical hardware (robots, sensors, IoT devices)
- This script simulates that hardware by sending HTTP requests
- The API treats this script exactly like a real device (uses X-DEVICE-KEY header)
- This removes the need for physical hardware in a demo

HOW IT WORKS:
1. Generates realistic sensor values (temperature, acceleration, GPS)
2. Sends POST request to /api/ingest with X-DEVICE-KEY header
3. Repeats at specified rate (e.g., 5 readings per second)

AUTHENTICATION:
Devices authenticate via X-DEVICE-KEY header, not user sessions.
This is different from user authentication (which uses Flask sessions).
The API key comes from the devices table (created by seed script or admin panel).

WHY THIS EXISTS:
For a job demo, we can't require physical hardware.
This script proves the API works with device authentication,
and demonstrates how real devices would interact with the system.
"""

import argparse
import requests
import time
import random
import os
import sys
from datetime import datetime

DEFAULT_BASE_URL = "http://localhost:5001"

def generate_sensor_reading():
    """
    Generate a realistic sensor reading with random values.
    
    When called: For each reading to send (in the loop)
    Returns: Dictionary with sensor metrics
    
    Values are realistic:
    - Temperature: 20-45°C (room temp to hot)
    - Acceleration: -2 to 2 m/s² (normal movement)
    - Z acceleration: 9.5-10.0 (gravity, device at rest)
    - GPS: Turkey coordinates (39-40°N, 32-33°E)
    """
    return {
        "temperature_c": round(random.uniform(20.0, 45.0), 1),
        "accel_x": round(random.uniform(-2.0, 2.0), 3),
        "accel_y": round(random.uniform(-2.0, 2.0), 3),
        "accel_z": round(random.uniform(9.5, 10.0), 3),  # Gravity when at rest
        "latitude": round(random.uniform(39.0, 40.0), 4),
        "longitude": round(random.uniform(32.0, 33.0), 4)
    }

def send_reading(reading, base_url, device_key):
    """
    Send a sensor reading to the API with device authentication.
    
    When called: For each generated reading
    Returns: True if successful, False on error
    
    DEVICE AUTHENTICATION:
    - X-DEVICE-KEY header contains the device's API key
    - API looks up device by this key
    - Device identity determines which company owns the data
    
    This mimics how a real device would authenticate.
    Real devices would have the API key stored in firmware/config.
    """
    try:
        # POST request to ingest endpoint
        # X-DEVICE-KEY header authenticates the device
        # This is how devices prove their identity (different from user sessions)
        response = requests.post(
            f"{base_url}/api/ingest",
            json=reading,  # JSON payload with sensor data
            headers={
                "Content-Type": "application/json",
                "X-DEVICE-KEY": device_key  # Device authentication header
            },
            timeout=5
        )
        # Raise exception if HTTP error (4xx, 5xx)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending reading: {e}")
        return False

def main():
    """
    Main function: Parse arguments and generate sensor data.
    
    When called: From command line (python scripts/generate_data.py)
    Command line arguments:
    - --count: How many readings to generate
    - --rate: Readings per second
    - --device-key: Device API key (or use DEVICE_KEY env var)
    - --url: API base URL
    """
    parser = argparse.ArgumentParser(description="Generate fake sensor data for WESTINGEN")
    parser.add_argument("--count", type=int, default=200, help="Number of readings to generate")
    parser.add_argument("--rate", type=float, default=5, help="Readings per second")
    parser.add_argument("--device-key", type=str, help="Device API key (X-DEVICE-KEY header). Can also use DEVICE_KEY env var.")
    parser.add_argument("--url", type=str, default=DEFAULT_BASE_URL, help="Base URL of the API")
    
    args = parser.parse_args()
    base_url = args.url
    
    # Get device key from command line argument or environment variable
    # Environment variable is useful for scripts/automation
    device_key = args.device_key or os.getenv('DEVICE_KEY')
    if not device_key:
        print("❌ Error: --device-key argument or DEVICE_KEY environment variable required")
        print("   Run: python scripts/seed_demo.py to get a device API key")
        sys.exit(1)
    
    # Calculate delay between readings to achieve desired rate
    # If rate is 5/second, delay is 0.2 seconds between readings
    delay = 1.0 / args.rate
    success_count = 0
    error_count = 0
    
    print(f"Generating {args.count} readings at {args.rate} readings/second...")
    print(f"Target: {base_url}/api/ingest")
    print(f"Device Key: {device_key[:20]}...")  # Show first 20 chars for verification
    print("-" * 50)
    
    start_time = time.time()
    
    # Generate and send readings in a loop
    for i in range(args.count):
        # Generate one reading with random sensor values
        reading = generate_sensor_reading()
        
        # Send to API (with device authentication)
        if send_reading(reading, base_url, device_key):
            success_count += 1
            # Progress indicator every 10 readings
            if (i + 1) % 10 == 0:
                print(f"Sent {i + 1}/{args.count} readings...")
        else:
            error_count += 1
        
        # Wait before next reading (to achieve desired rate)
        if i < args.count - 1:
            time.sleep(delay)
    
    elapsed = time.time() - start_time
    
    # Print summary statistics
    print("-" * 50)
    print(f"Completed: {success_count} successful, {error_count} errors")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Average rate: {args.count / elapsed:.2f} readings/second")

if __name__ == "__main__":
    main()
