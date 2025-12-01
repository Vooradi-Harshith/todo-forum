from __future__ import annotations
from pydantic import BaseModel,ConfigDict
from datetime import datetime

class CommentCreate(BaseModel):
    content:str
    parent_id:int |None=None
class CommentRead(BaseModel):
    id:int
    content:str
    post_id:int
    user_id:int
    parent_id:int | None=None
    created_at:datetime
    model_config = ConfigDict(from_attributes=True)


class CommentList(BaseModel):
    items:list[CommentRead]
    total:int
    page:int=1
    page_size:int=10

class CommentTree(CommentRead):
    children: list["CommentTree"] = []
