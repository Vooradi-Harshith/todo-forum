# post.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    content: str
    image_data: Optional[str] = None # (You already had this)

class PostRead(BaseModel):
    id: int
    content: str
    thread_id: int
    user_id: int
    created_at: datetime
    image_data: Optional[str] = None # <--- ADD THIS LINE

    model_config = ConfigDict(
        from_attributes=True
    )

class PostList(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    page_size: int