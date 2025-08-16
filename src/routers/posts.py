from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from src.database import get_db
from src.models.blog import BlogPost
from src.models.user import User
from src.models.like import Like
from src.models.comment import Comment
from src.schemas.blog import (
    BlogPostCreate, 
    BlogPostUpdate, 
    BlogPost as BlogPostSchema,
    BlogPostWithDetails
)
from src.schemas.like import LikeResponse
from src.schemas.comment import CommentCreate, Comment as CommentSchema
from src.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=BlogPostSchema, status_code=status.HTTP_201_CREATED)
def create_blog_post(
    post: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_post = BlogPost(**post.dict(), author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Add counts
    db_post.like_count = 0
    db_post.comment_count = 0
    return db_post

@router.get("/", response_model=List[BlogPostWithDetails])
def read_blog_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(
        BlogPost,
        User.username.label('author_username'),
        func.count(Like.id.distinct()).label('like_count'),
        func.count(Comment.id.distinct()).label('comment_count')
    ).join(
        User, BlogPost.author_id == User.id
    ).outerjoin(
        Like, BlogPost.id == Like.post_id
    ).outerjoin(
        Comment, BlogPost.id == Comment.post_id
    ).group_by(BlogPost.id).offset(skip).limit(limit).all()
    
    result = []
    for post, author_username, like_count, comment_count in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_username": author_username,
            "like_count": like_count,
            "comment_count": comment_count
        }
        result.append(BlogPostWithDetails(**post_dict))
    
    return result

@router.get("/{post_id}", response_model=BlogPostWithDetails)
def read_blog_post(post_id: int, db: Session = Depends(get_db)):
    post_data = db.query(
        BlogPost,
        User.username.label('author_username'),
        func.count(Like.id.distinct()).label('like_count'),
        func.count(Comment.id.distinct()).label('comment_count')
    ).join(
        User, BlogPost.author_id == User.id
    ).outerjoin(
        Like, BlogPost.id == Like.post_id
    ).outerjoin(
        Comment, BlogPost.id == Comment.post_id
    ).filter(BlogPost.id == post_id).group_by(BlogPost.id).first()
    
    if post_data is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post, author_username, like_count, comment_count = post_data
    post_dict = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author_username": author_username,
        "like_count": like_count,
        "comment_count": comment_count
    }
    
    return BlogPostWithDetails(**post_dict)

@router.put("/{post_id}", response_model=BlogPostSchema)
def update_blog_post(
    post_id: int,
    post_update: BlogPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update only provided fields
    update_data = post_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    
    # Add counts
    like_count = db.query(Like).filter(Like.post_id == post_id).count()
    comment_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    db_post.like_count = like_count
    db_post.comment_count = comment_count
    
    return db_post

@router.delete("/{post_id}", response_model=dict)
def delete_blog_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    post_title = db_post.title  # Store title for success message
    db.delete(db_post)
    db.commit()
    
    return {
        "message": f"Post '{post_title}' deleted successfully",
        "post_id": post_id,
        "status": "success"
    }

@router.post("/{post_id}/like", response_model=LikeResponse)
def like_blog_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if post exists
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked the post
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    
    if existing_like:
        # Unlike the post
        db.delete(existing_like)
        db.commit()
        liked = False
        message = "Post unliked successfully"
    else:
        # Like the post
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        db.commit()
        liked = True
        message = "Post liked successfully"
    
    # Get total likes count
    total_likes = db.query(Like).filter(Like.post_id == post_id).count()
    
    return LikeResponse(
        message=message,
        liked=liked,
        total_likes=total_likes
    )

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
