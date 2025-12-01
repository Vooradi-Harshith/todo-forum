from datetime import datetime
from pydantic import BaseModel

class NotificationBase(BaseModel):
    message:str

class NotificationRead(NotificationBase):
    id:int
    user_id:int
    read:bool
    created_at:datetime

    class Config:
        from_attributes=True


class NotificationList(BaseModel):
    items:list[NotificationRead]
    total:int
    page:int
    page_size:int