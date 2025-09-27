-- Fix database schema to match the code expectations
USE civic_db;

-- Add missing columns if they don't exist
ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS title VARCHAR(255) DEFAULT 'Untitled Complaint';

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS pdf_url VARCHAR(500);

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS ai_urgency FLOAT DEFAULT 0.5;

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS priority_score FLOAT DEFAULT 0.0;

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS upvote_count INT DEFAULT 0;

ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Rename existing columns to match code expectations
ALTER TABLE complaints 
CHANGE COLUMN imageUrl image_url VARCHAR(500);

ALTER TABLE complaints 
CHANGE COLUMN createdAt created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add indexes for better performance
ALTER TABLE complaints 
ADD INDEX IF NOT EXISTS idx_priority_score (priority_score);

ALTER TABLE complaints 
ADD INDEX IF NOT EXISTS idx_upvote_count (upvote_count);

ALTER TABLE complaints 
ADD INDEX IF NOT EXISTS idx_user_id (user_id);

-- Create upvotes table if it doesn't exist
CREATE TABLE IF NOT EXISTS upvotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    complaint_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_complaint (user_id, complaint_id),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_complaint_id (complaint_id)
);


