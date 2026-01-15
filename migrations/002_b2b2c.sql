-- WESTINGEN B2B2C Migration
-- Adds multi-tenant support with companies, users, and devices
-- Run this second: psql westingen < migrations/002_b2b2c.sql

-- Companies Table
-- Represents tenants in the B2B2C model
-- Each company is isolated from others (multi-tenant architecture)
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,                    -- Unique company identifier
    name TEXT NOT NULL UNIQUE,                -- Company name (must be unique)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
-- Company employees who can log in and view data
-- Linked to company via company_id (tenant isolation)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    -- ON DELETE CASCADE: If company is deleted, delete all its users
    email TEXT UNIQUE NOT NULL,               -- Login email (must be unique across all companies)
    password_hash TEXT NOT NULL,              -- Hashed password (never store plain passwords)
    role TEXT NOT NULL CHECK (role IN ('owner', 'manager', 'operator')),
    -- CHECK constraint: Role must be one of these values
    -- owner: Can create devices, full access
    -- manager: (future: can view but not create)
    -- operator: (future: read-only access)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices Table
-- Physical or simulated devices that send sensor data
-- Linked to company via company_id (tenant isolation)
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    -- ON DELETE CASCADE: If company is deleted, delete all its devices
    name TEXT NOT NULL,                       -- Device name (e.g., "robot-001")
    api_key TEXT UNIQUE NOT NULL,            -- API key for device authentication (X-DEVICE-KEY header)
    -- UNIQUE: Each API key must be unique (prevents collisions)
    -- Devices use this key to authenticate, not user sessions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modify sensor_readings table
-- Add tenant isolation columns to existing table
ALTER TABLE sensor_readings 
    ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    -- company_id: Links reading to company (tenant isolation)
    -- ON DELETE CASCADE: If company deleted, delete all its readings
    ADD COLUMN IF NOT EXISTS device_id_fk INTEGER REFERENCES devices(id) ON DELETE SET NULL;
    -- device_id_fk: Foreign key to devices table (proper relational link)
    -- ON DELETE SET NULL: If device deleted, keep reading but set FK to NULL
    -- device_id (text) kept for backward compatibility, but device_id_fk is preferred

-- Indexes for Performance
-- Indexes speed up queries that filter or sort by these columns

-- Composite index: company_id + created_at
-- Used by /api/latest and /api/stats (filter by company, order by time)
-- Most common query pattern: "Show recent readings for my company"
CREATE INDEX IF NOT EXISTS idx_sensor_readings_company_created ON sensor_readings(company_id, created_at DESC);

-- Index on api_key: Speeds up device authentication lookup
-- Used by /api/ingest to find device by X-DEVICE-KEY header
-- UNIQUE constraint already creates an index, but explicit for clarity
CREATE INDEX IF NOT EXISTS idx_devices_api_key ON devices(api_key);

-- Index on email: Speeds up login lookup
-- Used during login to find user by email
-- UNIQUE constraint already creates an index, but explicit for clarity
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Index on company_id in users: Speeds up "find all users for company"
-- Useful for admin queries (though not used in this demo)
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);
