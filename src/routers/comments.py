from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from src.database import get_db
from src.models.comment import Comment
from src.models.user import User
from src.models.blog import BlogPost
from src.schemas.comment import CommentCreate, Comment as CommentSchema
from src.dependencies import get_current_user

router = APIRouter()

@router.post("/{post_id}/comment", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if post exists
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create comment
    db_comment = Comment(
        content=comment.content,
        user_id=current_user.id,
        post_id=post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Add username to response
    db_comment.username = current_user.username
    return db_comment

@router.get("/{post_id}/comments", response_model=List[CommentSchema])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get comments with usernames
    comments = db.query(Comment, User.username).join(
        User, Comment.user_id == User.id
    ).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).all()
    
    result = []
    for comment, username in comments:
        comment_dict = {
            "id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "created_at": comment.created_at,
            "username": username
        }
        result.append(CommentSchema(**comment_dict))
    
    return result
