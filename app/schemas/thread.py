from datetime import datetime
from pydantic import BaseModel

class ThreadBase(BaseModel):
    title:str
    content:str

class ThreadCreate(ThreadBase):
    pass 
class ThreadRead(ThreadBase):
    id:int
    owner_id:int
    created_at:datetime

    class Config:
        orm_mode=True

class ThreadList(BaseModel):
    items:list[ThreadRead]
    total:int
    page:int
    page_size:int

    class Config:
        orm_mode=True