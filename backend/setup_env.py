# backend/setup_env.py
# Simple script to help create the .env file

import os

def create_env_file():
    """Create a .env file from user input"""
    
    print("🔧 Setting up your database configuration...")
    print("This will create a .env file with your database settings.\n")
    
    # Get user input
    host = input("Database host (default: localhost): ").strip() or "localhost"
    user = input("Database user (default: root): ").strip() or "root"
    password = input("Database password: ").strip()
    database = input("Database name (default: civic_db): ").strip() or "civic_db"
    port = input("Database port (default: 3306): ").strip() or "3306"
    
    # Create .env content
    env_content = f"""DB_HOST={host}
DB_USER={user}
DB_PASSWORD={password}
DB_NAME={database}
DB_PORT={port}
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("📁 Location: backend/.env")
        print("\n⚠️  Remember: Never commit the .env file to version control!")
        
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file()
