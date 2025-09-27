-- Add updated_at column to complaints table
-- This script adds an updated_at timestamp column that automatically updates when the record is modified

ALTER TABLE complaints 
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Update existing records to have updated_at set to created_at
UPDATE complaints 
SET updated_at = created_at 
WHERE updated_at IS NULL;
