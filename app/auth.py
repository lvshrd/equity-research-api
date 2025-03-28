# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.database import get_db_connection
from typing import Optional, Dict, Any, Union
from config.config_load import CONFIG
from app.jwt_auth import get_current_user_jwt

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

async def get_current_user_from_token_or_api_key(
    token_user: Optional[Dict[str, Any]] = Depends(get_current_user_jwt),
    api_key: Dict[str, Any] = Depends(api_key_header)
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
    # Try JWT token first
    if token_user is not None:
        return token_user
    
    # If no valid token, try API key
    if api_key:
        user = await get_user_from_api_key(api_key)
        if user:
            return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )