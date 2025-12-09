from typing import Optional
from fastapi import Header, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.auth import TokenPayload

# Note: We don't strictly need 'db' here unless you want to verify the user exists in DB.
# For just extracting the ID from the token, this is sufficient and faster.

def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[int]:
    """
    Extracts user_id from the Authorization header if present.
    Returns None if header is missing or invalid.
    Does NOT raise 401 (that is for required_auth).
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = TokenPayload(**payload)
        return token_data.sub
    except (JWTError, ValueError):
        # If token is expired or invalid, we treat them as a guest (None)
        # rather than crashing.
        return None