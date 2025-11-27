from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PostCreate(BaseModel):
    content: str

class PostRead(BaseModel):
    id: int
    content: str
    thread_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)   # ← THIS is required for ORM Support


class PostList(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    page_size: int
