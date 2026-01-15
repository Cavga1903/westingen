-- WESTINGEN Sensor Readings Table
-- Run this migration to create the sensor_readings table

CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id TEXT NOT NULL,
    temperature_c FLOAT NOT NULL,
    accel_x FLOAT NOT NULL,
    accel_y FLOAT NOT NULL,
    accel_z FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_created_at ON sensor_readings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_id ON sensor_readings(device_id);
