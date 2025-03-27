# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from config import CONFIG

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key():
    return CONFIG["app"]["API_KEY"]

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header is missing"
        )
    
    valid_api_key = get_api_key()
    if api_key != valid_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    return api_key