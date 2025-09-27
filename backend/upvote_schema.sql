-- Create upvotes table to track user votes and prevent duplicates
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

-- Add upvote_count column to complaints table if it doesn't exist
ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS upvote_count INT DEFAULT 0;

-- Add user_id column to complaints table to track who created the complaint
ALTER TABLE complaints 
ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Add index for better performance on upvote_count queries
ALTER TABLE complaints 
ADD INDEX IF NOT EXISTS idx_upvote_count (upvote_count);

-- Add index for user_id queries
ALTER TABLE complaints 
ADD INDEX IF NOT EXISTS idx_user_id (user_id);
