// Firebase Console Script for Admin Role Setup
// Run this in the Firebase Console browser console

// Function to set admin role for a user
function setAdminRole(userEmail) {
    // Get the current user
    const user = firebase.auth().currentUser;
    
    if (!user) {
        console.error('No user logged in');
        return;
    }
    
    // Set custom claims
    user.getIdToken(true).then((idToken) => {
        // This would typically be done server-side
        console.log('ID Token:', idToken);
        console.log('To set admin role, use the Firebase Admin SDK on the server');
    });
}

// Function to check if user has admin role
function checkAdminRole() {
    const user = firebase.auth().currentUser;
    
    if (!user) {
        console.error('No user logged in');
        return;
    }
    
    user.getIdTokenResult().then((idTokenResult) => {
        const claims = idTokenResult.claims;
        console.log('User claims:', claims);
        
        if (claims.admin) {
            console.log('✅ User has admin role');
        } else {
            console.log('❌ User does not have admin role');
        }
    });
}

// Function to list all users (requires admin privileges)
function listUsers() {
    // This would typically be done server-side with Firebase Admin SDK
    console.log('To list users, use the Firebase Admin SDK on the server');
}

// Usage examples:
console.log('Available functions:');
console.log('- setAdminRole(userEmail)');
console.log('- checkAdminRole()');
console.log('- listUsers()');

// Example usage:
// setAdminRole('admin@example.com');
// checkAdminRole();
