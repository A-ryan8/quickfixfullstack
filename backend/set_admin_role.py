#!/usr/bin/env python3
"""
Script to set admin role for a user in Firebase
"""

import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        print("✅ Firebase already initialized")
        return True
    except ValueError:
        # Initialize Firebase
        try:
            # Try to use service account key file
            if os.path.exists("firebase-service-account.json"):
                cred = credentials.Certificate("firebase-service-account.json")
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized with service account key")
                return True
            else:
                print("❌ Firebase service account key file not found")
                print("Please download firebase-service-account.json from Firebase Console")
                return False
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            return False

def set_admin_role(user_email):
    """Set admin role for a user"""
    try:
        # Get user by email
        user = auth.get_user_by_email(user_email)
        print(f"✅ Found user: {user.uid} ({user.email})")
        
        # Set custom claims for admin role
        auth.set_custom_user_claims(user.uid, {'admin': True})
        print(f"✅ Admin role set for user: {user.email}")
        
        # Verify the role was set
        user = auth.get_user(user.uid)
        custom_claims = user.custom_claims
        if custom_claims and custom_claims.get('admin'):
            print("✅ Admin role verified successfully")
            return True
        else:
            print("❌ Admin role not set properly")
            return False
            
    except auth.UserNotFoundError:
        print(f"❌ User not found: {user_email}")
        return False
    except Exception as e:
        print(f"❌ Error setting admin role: {e}")
        return False

def list_users():
    """List all users in Firebase"""
    try:
        print("📋 Listing all users:")
        print("-" * 50)
        
        page = auth.list_users()
        for user in page.users:
            custom_claims = user.custom_claims or {}
            admin_status = "👑 ADMIN" if custom_claims.get('admin') else "👤 USER"
            print(f"{admin_status} | {user.email} | UID: {user.uid}")
            
        return True
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return False

def main():
    """Main function"""
    print("🔐 Firebase Admin Role Setup")
    print("=" * 50)
    
    # Initialize Firebase
    if not initialize_firebase():
        return
    
    while True:
        print("\nOptions:")
        print("1. Set admin role for user")
        print("2. List all users")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            email = input("Enter user email: ").strip()
            if email:
                set_admin_role(email)
            else:
                print("❌ Please enter a valid email")
                
        elif choice == "2":
            list_users()
            
        elif choice == "3":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

