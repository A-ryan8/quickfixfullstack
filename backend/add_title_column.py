#!/usr/bin/env python3
"""
Script to add title column to complaints table
"""
import mysql.connector
from config import DB_CONFIG

def add_title_column():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Add title column
        cursor.execute("ALTER TABLE complaints ADD COLUMN title VARCHAR(255) DEFAULT NULL")
        connection.commit()
        
        print("✅ Successfully added 'title' column to complaints table")
        
        # Verify the column was added
        cursor.execute("DESCRIBE complaints")
        columns = cursor.fetchall()
        
        print("\n📋 Current table structure:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
            
    except mysql.connector.Error as e:
        if e.errno == 1060:  # Duplicate column name
            print("⚠️  Column 'title' already exists in complaints table")
        else:
            print(f"❌ Error adding title column: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_title_column()

