#!/usr/bin/env python3
"""
Script to add updated_at column to complaints table
"""
import mysql.connector
from config import DB_CONFIG

def add_updated_at_column():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Add updated_at column
        cursor.execute("""
            ALTER TABLE complaints 
            ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        """)
        print("Added updated_at column successfully")
        
        # Update existing records to have updated_at = created_at
        cursor.execute("""
            UPDATE complaints 
            SET updated_at = created_at 
            WHERE updated_at IS NULL
        """)
        print(f"Updated {cursor.rowcount} existing records")
        
        # Commit changes
        conn.commit()
        print("Changes committed successfully")
        
    except mysql.connector.Error as e:
        if e.errno == 1060:  # Column already exists
            print("Column 'updated_at' already exists")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    add_updated_at_column()
