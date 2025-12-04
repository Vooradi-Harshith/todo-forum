from pydantic import BaseModel, EmailStr
from typing import Optional


# Nested Role Schema
class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Optional[RoleRead] = None  # <--- Crucial: Include this!

    class Config:
        from_attributes = True
