#!/usr/bin/env python3
"""
Script to fix the database schema to match the code expectations
"""

import mysql.connector
from config import DB_CONFIG

def fix_database_schema():
    """Fix the database schema to match code expectations"""
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ Connected to MySQL database")
        
        # Use the civic_db database
        cursor.execute("USE civic_db")
        print("✅ Using civic_db database")
        
        # Check if complaints table exists
        cursor.execute("SHOW TABLES LIKE 'complaints'")
        if not cursor.fetchone():
            print("❌ Complaints table does not exist. Creating it...")
            cursor.execute("""
                CREATE TABLE complaints (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) DEFAULT 'Untitled Complaint',
                    description TEXT NOT NULL,
                    location VARCHAR(255) NOT NULL,
                    image_url VARCHAR(500),
                    pdf_url VARCHAR(500),
                    status VARCHAR(50) DEFAULT 'New',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    ai_urgency FLOAT DEFAULT 0.5,
                    priority_score FLOAT DEFAULT 0.0,
                    upvote_count INT DEFAULT 0,
                    user_id VARCHAR(255)
                )
            """)
            print("✅ Created complaints table")
        else:
            print("✅ Complaints table exists, updating schema...")
            
            # Add missing columns
            columns_to_add = [
                ("title", "VARCHAR(255) DEFAULT 'Untitled Complaint'"),
                ("image_url", "VARCHAR(500)"),
                ("pdf_url", "VARCHAR(500)"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                ("ai_urgency", "FLOAT DEFAULT 0.5"),
                ("priority_score", "FLOAT DEFAULT 0.0"),
                ("upvote_count", "INT DEFAULT 0"),
                ("user_id", "VARCHAR(255)")
            ]
            
            for column_name, column_def in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE complaints ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except mysql.connector.Error as e:
                    if "Duplicate column name" in str(e):
                        print(f"⚠️  Column {column_name} already exists")
                    else:
                        print(f"❌ Error adding column {column_name}: {e}")
            
            # Rename existing columns if they exist
            try:
                cursor.execute("ALTER TABLE complaints CHANGE COLUMN imageUrl image_url VARCHAR(500)")
                print("✅ Renamed imageUrl to image_url")
            except mysql.connector.Error as e:
                if "Unknown column" in str(e):
                    print("⚠️  imageUrl column doesn't exist, skipping rename")
                else:
                    print(f"❌ Error renaming imageUrl: {e}")
            
            try:
                cursor.execute("ALTER TABLE complaints CHANGE COLUMN createdAt created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("✅ Renamed createdAt to created_at")
            except mysql.connector.Error as e:
                if "Unknown column" in str(e):
                    print("⚠️  createdAt column doesn't exist, skipping rename")
                else:
                    print(f"❌ Error renaming createdAt: {e}")
        
        # Create upvotes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upvotes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                complaint_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_complaint (user_id, complaint_id),
                FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_complaint_id (complaint_id)
            )
        """)
        print("✅ Created/verified upvotes table")
        
        # Add indexes for better performance
        indexes = [
            ("idx_priority_score", "priority_score"),
            ("idx_upvote_count", "upvote_count"),
            ("idx_user_id", "user_id")
        ]
        
        for index_name, column_name in indexes:
            try:
                cursor.execute(f"ALTER TABLE complaints ADD INDEX {index_name} ({column_name})")
                print(f"✅ Added index: {index_name}")
            except mysql.connector.Error as e:
                if "Duplicate key name" in str(e):
                    print(f"⚠️  Index {index_name} already exists")
                else:
                    print(f"❌ Error adding index {index_name}: {e}")
        
        # Commit changes
        connection.commit()
        print("✅ Database schema updated successfully!")
        
        # Show current table structure
        cursor.execute("DESCRIBE complaints")
        columns = cursor.fetchall()
        print("\n📋 Current complaints table structure:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Database connection closed")
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing Database Schema")
    print("=" * 40)
    success = fix_database_schema()
    
    if success:
        print("\n🎉 Database schema fixed successfully!")
        print("You can now run the backend server.")
    else:
        print("\n❌ Failed to fix database schema")
        print("Please check the error messages above.")


