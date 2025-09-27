#!/usr/bin/env python3
"""
Script to clean up duplicate columns in the database
"""

import mysql.connector
from config import DB_CONFIG

def cleanup_duplicate_columns():
    """Remove duplicate columns from the complaints table"""
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ Connected to MySQL database")
        
        # Use the civic_db database
        cursor.execute("USE civic_db")
        print("✅ Using civic_db database")
        
        # Check if we have duplicate columns
        cursor.execute("DESCRIBE complaints")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        print(f"📋 Current columns: {column_names}")
        
        # Remove old columns if new ones exist
        if 'image_url' in column_names and 'imageUrl' in column_names:
            print("🔄 Removing old imageUrl column...")
            cursor.execute("ALTER TABLE complaints DROP COLUMN imageUrl")
            print("✅ Removed imageUrl column")
        
        if 'pdf_url' in column_names and 'pdfUrl' in column_names:
            print("🔄 Removing old pdfUrl column...")
            cursor.execute("ALTER TABLE complaints DROP COLUMN pdfUrl")
            print("✅ Removed pdfUrl column")
        
        # Commit changes
        connection.commit()
        print("✅ Duplicate columns cleaned up successfully!")
        
        # Show final table structure
        cursor.execute("DESCRIBE complaints")
        columns = cursor.fetchall()
        print("\n📋 Final complaints table structure:")
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
    print("🧹 Cleaning Up Duplicate Columns")
    print("=" * 40)
    success = cleanup_duplicate_columns()
    
    if success:
        print("\n🎉 Database cleanup completed successfully!")
    else:
        print("\n❌ Failed to cleanup database")


