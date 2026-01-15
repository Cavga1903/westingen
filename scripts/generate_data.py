#!/usr/bin/env python3
"""
WESTINGEN Fake Data Generator
Generates realistic sensor data and sends it to the /api/ingest endpoint.
"""

import argparse
import requests
import time
import random
from datetime import datetime

DEFAULT_BASE_URL = "http://localhost:5001"

def generate_sensor_reading(device_id):
    """Generate a realistic sensor reading."""
    return {
        "device_id": device_id,
        "temperature_c": round(random.uniform(20.0, 45.0), 1),
        "accel_x": round(random.uniform(-2.0, 2.0), 3),
        "accel_y": round(random.uniform(-2.0, 2.0), 3),
        "accel_z": round(random.uniform(9.5, 10.0), 3),
        "latitude": round(random.uniform(39.0, 40.0), 4),
        "longitude": round(random.uniform(32.0, 33.0), 4)
    }

def send_reading(reading, base_url):
    """Send a reading to the API."""
    try:
        response = requests.post(
            f"{base_url}/api/ingest",
            json=reading,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending reading: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate fake sensor data for WESTINGEN")
    parser.add_argument("--count", type=int, default=200, help="Number of readings to generate")
    parser.add_argument("--rate", type=float, default=5, help="Readings per second")
    parser.add_argument("--device", type=str, default="robot-001", help="Device ID")
    parser.add_argument("--url", type=str, default=DEFAULT_BASE_URL, help="Base URL of the API")
    
    args = parser.parse_args()
    base_url = args.url
    
    device_ids = [f"robot-{i:03d}" for i in range(1, 6)]
    
    delay = 1.0 / args.rate
    success_count = 0
    error_count = 0
    
    print(f"Generating {args.count} readings at {args.rate} readings/second...")
    print(f"Target: {base_url}/api/ingest")
    print("-" * 50)
    
    start_time = time.time()
    
    for i in range(args.count):
        device_id = random.choice(device_ids)
        reading = generate_sensor_reading(device_id)
        
        if send_reading(reading, base_url):
            success_count += 1
            if (i + 1) % 10 == 0:
                print(f"Sent {i + 1}/{args.count} readings...")
        else:
            error_count += 1
        
        if i < args.count - 1:
            time.sleep(delay)
    
    elapsed = time.time() - start_time
    
    print("-" * 50)
    print(f"Completed: {success_count} successful, {error_count} errors")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Average rate: {args.count / elapsed:.2f} readings/second")

if __name__ == "__main__":
    main()
