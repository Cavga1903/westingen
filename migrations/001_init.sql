-- WESTINGEN Initial Migration
-- Creates the core sensor_readings table
-- Run this first: psql westingen < migrations/001_init.sql

-- Sensor Readings Table
-- Stores all sensor data from devices
-- This is the core data table - everything else supports this
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,                    -- Auto-incrementing unique ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When reading was received
    device_id TEXT NOT NULL,                   -- Device identifier (text for flexibility)
    temperature_c FLOAT NOT NULL,              -- Temperature in Celsius
    accel_x FLOAT NOT NULL,                    -- X-axis acceleration (m/s²)
    accel_y FLOAT NOT NULL,                    -- Y-axis acceleration (m/s²)
    accel_z FLOAT NOT NULL,                    -- Z-axis acceleration (m/s², includes gravity)
    latitude FLOAT NOT NULL,                   -- GPS latitude
    longitude FLOAT NOT NULL                   -- GPS longitude
);

-- Index on created_at: Speeds up queries that order by time
-- DESC order: Most recent first (common query pattern)
CREATE INDEX IF NOT EXISTS idx_sensor_readings_created_at ON sensor_readings(created_at DESC);

-- Index on device_id: Speeds up queries filtering by device
-- Useful for "show all readings from device X"
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_id ON sensor_readings(device_id);
