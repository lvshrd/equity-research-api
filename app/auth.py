# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.database import get_db_connection
from typing import Optional, Dict, Any, Union
from config.config_load import CONFIG
from app.jwt_auth import get_current_user_jwt, get_default_user

# API key header extractor
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_user_from_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from API key
    
    Args:
        api_key: The API key to validate
        
    Returns:
        User information if API key is valid, None otherwise
    """
    if not api_key:
        return None
    
    # Check if API key matches the one in config
    if api_key == CONFIG["app"]["API_KEY"]:
        # Return default user for simplified authentication
        return get_default_user()
    
    # If not using default API key, check database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, username 
                FROM users 
                WHERE api_key = %s AND is_active = TRUE
                """,
                (api_key,)
            )
            user = cursor.fetchone()
            return user
    except Exception:
        return None
    finally:
        conn.close()

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verify API key and return user information
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        User information if API key is valid
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header is missing"
        )
    
    user = await get_user_from_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    return user

async def get_current_user_from_token_or_api_key(
    token_user: Dict[str, Any] = Depends(get_current_user_jwt),
    api_key_user: Dict[str, Any] = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get current user from either JWT token or API key
    
    This function tries to authenticate using JWT token first,
    and falls back to API key if token authentication fails.
    
    Args:
        token_user: User from JWT token
        api_key_user: User from API key
        
    Returns:
        User information from either source
    """
    # If token authentication succeeded, use that user
    if token_user:
        return token_user
    
    # Otherwise, use API key user
    return api_key_user