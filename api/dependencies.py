# api/dependencies.py # Common dependencies (get_db, auth, etc.)
from fastapi import Header, HTTPException, status
from settings import get_settings
from db.database_connection import get_db

settings = get_settings()
get_db = get_db
        
def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """ Verify API key from Header """
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return x_api_key
    