from fastapi import Depends,HTTPException
from app.models.user import User
from app.api.v1.auth import get_current_user

def required_admin(current_user:User=Depends(get_current_user)):
    if current_user.role.name!='admin':
        raise HTTPException(status_code=403, detail='admin access required')  # 🔥 instead of return
    return current_user
