from pydantic import BaseModel
from datetime import datetime
from typing import List

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    username: str

    class Config:
        from_attributes = True
