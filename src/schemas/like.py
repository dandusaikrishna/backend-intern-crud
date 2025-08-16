from pydantic import BaseModel
from datetime import datetime

class LikeCreate(BaseModel):
    pass

class Like(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    message: str
    liked: bool
    total_likes: int
