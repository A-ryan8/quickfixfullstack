# How to Add Admin Role to Users

## Method 1: Firebase Console (Easiest)

1. **Go to Firebase Console**: https://console.firebase.google.com
2. **Select your project**
3. **Go to Authentication > Users**
4. **Find the user** you want to make an admin
5. **Click on the user** to open their details
6. **Look for "Custom Claims"** section
7. **Click "Add custom claim"**
8. **Add the role claim**:
   - **Key**: `role`
   - **Value**: `admin`
9. **Click "Save"**

## Method 2: Using the Setup Script

1. **Install Firebase Admin SDK** (if not already installed):
   ```bash
   pip install firebase-admin
   ```

2. **Set up Firebase Admin credentials**:
   - Go to Firebase Console > Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
     ```

3. **Run the setup script**:
   ```bash
   cd backend
   python setup_admin.py
   ```
   
   Or specify the email directly:
   ```bash
   python setup_admin.py admin@example.com
   ```

## Method 3: Using Firebase CLI

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:
   ```bash
   firebase login
   ```

3. **Set custom claims** (requires Firebase Functions):
   ```javascript
   // In a Firebase Function
   admin.auth().setCustomUserClaims(uid, { role: 'admin' });
   ```

## Verifying Admin Role

After setting the admin role, the user needs to:

1. **Log out** from the app
2. **Log back in** to refresh their authentication token
3. **Test admin endpoints** to verify access

## Testing Admin Access

You can test if the admin role is working by:

1. **Using the test script**:
   ```bash
   python test_auth.py
   ```

2. **Checking the React dashboard** - admin users should see all complaints
3. **Testing API endpoints** - admin users should have access to all endpoints

## Troubleshooting

- **"User not found"**: Make sure the user exists in Firebase Authentication
- **"Permission denied"**: Check that the service account has proper permissions
- **"Token not refreshed"**: User must log out and log back in
- **"Still getting 403"**: Check that the custom claims are set correctly

## Security Notes

- Only grant admin roles to trusted users
- Admin roles are stored in Firebase custom claims
- Tokens are cached, so users need to refresh after role changes
- Consider implementing role expiration for security
