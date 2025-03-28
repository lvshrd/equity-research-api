# app/jwt_auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config.config_load import CONFIG
import uuid

# JWT settings
SECRET_KEY = CONFIG["app"].get("JWT_SECRET_KEY", CONFIG["app"]["API_KEY"])  # Fallback to API_KEY if JWT_SECRET_KEY not set
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Create the JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_jwt(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validate JWT token and return user information
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User information from token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # If no token provided, raise exception
    if not token:
        raise credentials_exception
    
    try:
        # Decode and validate the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user information
        user_id = payload.get("sub")
        username = payload.get("username", "default_user")
        
        if user_id is None:
            raise credentials_exception
            
        # Return user information
        return {"user_id": user_id, "username": username}
        
    except JWTError:
        raise credentials_exception

# Default user for simplified authentication
DEFAULT_USER = {
    "user_id": str(uuid.uuid4()),  # Generate a stable UUID
    "username": "default_user"
}

def get_default_user() -> Dict[str, str]:
    """
    Get default user information
    
    Returns:
        Default user dictionary
    """
    return DEFAULT_USER