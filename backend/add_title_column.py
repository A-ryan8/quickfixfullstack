#!/usr/bin/env python3
"""
Script to add title column to complaints table
"""

import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def add_title_column():
    """Add title column to complaints table"""
    try:
        # Database connection
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'civic_complaints')
        )
        
        cursor = connection.cursor()
        
        # Check if title column exists
        cursor.execute("SHOW COLUMNS FROM complaints LIKE 'title'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Title column already exists")
        else:
            # Add title column
            cursor.execute("ALTER TABLE complaints ADD COLUMN title VARCHAR(255) NOT NULL DEFAULT ''")
            connection.commit()
            print("✅ Title column added successfully")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error adding title column: {e}")

if __name__ == "__main__":
    add_title_column()
