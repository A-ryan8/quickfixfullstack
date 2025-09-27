#!/usr/bin/env python3
"""
Script to set up environment variables
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with default values"""
    env_content = """# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=civic_complaints

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your-client-cert-url

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Skipping .env file creation")
            return
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("📝 Please update the values in .env file with your actual configuration")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def create_env_template():
    """Create .env.template file"""
    template_content = """# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-db-password
DB_NAME=civic_complaints

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your-client-cert-url

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key
"""
    
    template_file = Path(".env.template")
    
    try:
        with open(template_file, 'w') as f:
            f.write(template_content)
        print("✅ .env.template file created successfully")
    except Exception as e:
        print(f"❌ Error creating .env.template file: {e}")

def main():
    """Main function"""
    print("🔧 Environment Setup")
    print("=" * 30)
    
    create_env_file()
    create_env_template()
    
    print("\n📋 Next steps:")
    print("1. Update .env file with your actual configuration")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the server: python main_simple_complaints.py")

if __name__ == "__main__":
    main()
