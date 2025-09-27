#!/usr/bin/env python3
"""
Script to add updated_at column to complaints table
"""

import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def add_updated_at_column():
    """Add updated_at column to complaints table"""
    try:
        # Database connection
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'civic_complaints')
        )
        
        cursor = connection.cursor()
        
        # Check if updated_at column exists
        cursor.execute("SHOW COLUMNS FROM complaints LIKE 'updated_at'")
        result = cursor.fetchone()
        
        if result:
            print("✅ updated_at column already exists")
        else:
            # Add updated_at column
            cursor.execute("ALTER TABLE complaints ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            connection.commit()
            print("✅ updated_at column added successfully")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error adding updated_at column: {e}")

if __name__ == "__main__":
    add_updated_at_column()
