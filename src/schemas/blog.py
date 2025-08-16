from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class BlogPostBase(BaseModel):
    title: str
    content: str

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BlogPostBase):
    title: Optional[str] = None
    content: Optional[str] = None

class BlogPost(BlogPostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    like_count: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True

class BlogPostWithDetails(BlogPost):
    author_username: str
