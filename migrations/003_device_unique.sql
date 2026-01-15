-- WESTINGEN Device Name Unique Constraint
-- Ensures device names are unique within each company
-- Run: psql westingen < migrations/003_device_unique.sql

-- Add unique constraint on (company_id, name)
-- This prevents duplicate device names within the same company
-- Different companies can have devices with the same name
CREATE UNIQUE INDEX IF NOT EXISTS idx_devices_company_name_unique 
ON devices(company_id, name);
