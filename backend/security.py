"""
Security module for FastAPI backend with Firebase JWT authentication and role-based authorization.
"""

import json
import requests
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()

# Firebase configuration
FIREBASE_PROJECT_ID = "quickfix-a050e"
FIREBASE_PUBLIC_KEYS_URL = f"https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"

# Cache for Firebase public keys
_firebase_keys_cache = None
_keys_cache_expiry = None

def get_firebase_public_keys() -> Dict[str, str]:
    """
    Fetch Firebase public keys for JWT verification.
    Uses caching to avoid repeated requests.
    """
    global _firebase_keys_cache, _keys_cache_expiry
    
    import time
    current_time = time.time()
    
    # Return cached keys if still valid (cache for 1 hour)
    if _firebase_keys_cache and _keys_cache_expiry and current_time < _keys_cache_expiry:
        return _firebase_keys_cache
    
    try:
        response = requests.get(FIREBASE_PUBLIC_KEYS_URL, timeout=10)
        response.raise_for_status()
        
        _firebase_keys_cache = response.json()
        _keys_cache_expiry = current_time + 3600  # Cache for 1 hour
        
        logger.info("Firebase public keys fetched and cached successfully")
        return _firebase_keys_cache
        
    except Exception as e:
        logger.error(f"Failed to fetch Firebase public keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )

def verify_firebase_token(token: str) -> Dict[str, Any]:
    """
    Verify Firebase JWT token and return decoded payload.
    """
    try:
        from jwt import PyJWKClient
        
        # Get Firebase public keys
        public_keys = get_firebase_public_keys()
        
        # Decode token header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header.get('kid')
        
        if not key_id or key_id not in public_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key ID not found"
            )
        
        # Get the public key
        public_key = public_keys[key_id]
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=FIREBASE_PROJECT_ID,
            issuer=f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}"
        )
        
        logger.info(f"Token verified successfully for user: {payload.get('uid', 'unknown')}")
        return payload
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from Firebase JWT token.
    This is the basic authentication dependency.
    """
    try:
        token = credentials.credentials
        payload = verify_firebase_token(token)
        
        # Extract user information from token
        user_data = {
            "uid": payload.get("uid"),
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified", False),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
            "role": payload.get("role", "user"),  # Default role is 'user'
            "custom_claims": payload.get("custom_claims", {})
        }
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated user and verify they have admin role.
    This is the admin-only authentication dependency.
    """
    # Check if user has admin role
    user_role = current_user.get("role", "user")
    
    if user_role != "admin":
        logger.warning(f"Non-admin user attempted admin access: {current_user.get('email', 'unknown')} (role: {user_role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger.info(f"Admin access granted to: {current_user.get('email', 'unknown')}")
    return current_user

def get_current_admin_user_bypass() -> Dict[str, Any]:
    """
    Temporary bypass for admin authentication - allows any request through
    TODO: Remove this in production
    """
    logger.warning("Using admin bypass - this should not be used in production!")
    return {
        "uid": "bypass_user",
        "email": "admin@bypass.com",
        "role": "admin",
        "name": "Bypass Admin"
    }

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Optional authentication dependency that returns user data if authenticated,
    or None if not authenticated. Useful for endpoints that work for both
    authenticated and anonymous users.
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

# Role-based dependencies for different access levels
def require_role(required_role: str):
    """
    Create a dependency that requires a specific role.
    Usage: Depends(require_role("admin"))
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        
        if user_role != required_role:
            logger.warning(f"User with role '{user_role}' attempted to access '{required_role}' endpoint")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.title()} access required"
            )
        
        return current_user
    
    return role_checker

# Predefined role dependencies
require_admin = require_role("admin")
require_moderator = require_role("moderator")
require_user = require_role("user")
