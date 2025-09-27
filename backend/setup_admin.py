#!/usr/bin/env python3
"""
Script to set admin role for a user using Firebase Admin SDK
Run this script to grant admin privileges to a specific user.
"""

import os
import sys
import json
from firebase_admin import initialize_app, auth, credentials
from firebase_admin.exceptions import FirebaseError

def setup_firebase_admin():
    """Initialize Firebase Admin SDK"""
    try:
        # Try to get the default app first
        app = initialize_app()
        print("✅ Firebase Admin SDK initialized successfully")
        return app
    except ValueError:
        # App already exists
        print("✅ Firebase Admin SDK already initialized")
        return None

def set_admin_role(email: str):
    """Set admin role for a user by email"""
    try:
        # Get user by email
        user = auth.get_user_by_email(email)
        print(f"✅ Found user: {user.email} (UID: {user.uid})")
        
        # Set custom claims
        custom_claims = {
            'role': 'admin'
        }
        
        auth.set_custom_user_claims(user.uid, custom_claims)
        print(f"✅ Successfully set admin role for {email}")
        
        # Verify the claims were set
        updated_user = auth.get_user(user.uid)
        print(f"✅ User claims: {updated_user.custom_claims}")
        
    except auth.UserNotFoundError:
        print(f"❌ User with email {email} not found")
        return False
    except FirebaseError as e:
        print(f"❌ Firebase error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🔧 Firebase Admin Role Setup")
    print("=" * 40)
    
    # Initialize Firebase
    setup_firebase_admin()
    
    # Get email from command line or prompt
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter the email of the user to make admin: ").strip()
    
    if not email:
        print("❌ Email is required")
        return
    
    # Set admin role
    success = set_admin_role(email)
    
    if success:
        print("\n🎉 Admin role setup complete!")
        print(f"User {email} now has admin privileges.")
        print("\nNext steps:")
        print("1. The user should log out and log back in to refresh their token")
        print("2. Test the admin endpoints to verify access")
    else:
        print("\n❌ Failed to set admin role")
        print("Please check the error messages above and try again")

if __name__ == "__main__":
    main()


