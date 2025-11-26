from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserCreate, UserRead, Token, LoginIn
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import settings


router=APIRouter(prefix='/auth',tags=['auth'])
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/auth/token')


#Register

@router.post('/register',response_model=UserRead,status_code=status.HTTP_201_CREATED)

def register_user(payload:UserCreate,db:Session = Depends(get_db)):
    existing=db.query(User).filter((User.username==payload.username) |(User.email==payload.email)).first()
    if existing:
        raise HTTPException(status_code=400,detail='username or email already exists')

    role=db.query(Role).filter(Role.name=='member').first()
    if not role:
        role=Role(name="member")
        db.add(role)
        db.flush()

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

    # Token endpoint (OAuth2 password flow compatible)

@router.post('/token',response_model=Token)
def login_for_access_token(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    # form_data.username and form_data.password
    user=db.query(User).filter(User.username==form_data.username).first()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username or password',
                            headers={'WWW-Authenticate':'Bearer'})
    access_token_expires=timedelta(minutes=settings.ACCES_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(subject=str(user.id),expires_delta=access_token_expires)
    return {'access_token':access_token,'token_type':'bearer'}

# Helper to get current user

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db))->User:
    try:
        payload=decode_access_token(token)
        user_id:str=payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid authentication credentials')
        
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    user=db.query(User).filter(User.id==int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# Small helper - role check (callable)
def require_role(role_name: str):
    def _require_role(current_user: User = Depends(get_current_user)):
        if not current_user.role or current_user.role.name != role_name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return _require_role
       