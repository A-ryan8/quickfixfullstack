-- Add updated_at column to complaints table
ALTER TABLE complaints ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Update existing records to have updated_at = created_at
UPDATE complaints SET updated_at = created_at WHERE updated_at IS NULL;
