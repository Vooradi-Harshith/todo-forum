from datetime import datetime,timedelta,timezone
from typing import Optional

from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")



#password hashing helpers
def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(password:str,hashed_password:str)->bool:
    return pwd_context.verify(password,hashed_password)


#jwt helpers

def create_access_token(
        subject:str,
        expires_delta:Optional[timedelta]=None,
)->str:
    expire=datetime.now(timezone.utc)+(expires_delta or timedelta(minutes=settings.ACCES_TOKEN_EXPIRE_MINUTES))
    to_encode={"exp":expire,"sub":str(subject)}
    encoded_jwt=jwt.encode(to_encode,settings.JWT_SECRET,algorithm=settings.JWT_ALGO)
    return encoded_jwt
def decode_access_token(token:str)->dict:
    payload=jwt.decode(token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGO])
    return payload
