from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from src.database import engine, Base
from src.routers import auth, posts, comments

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LawVriksh Blog Management System",
    description="A blog management system with CRUD operations, likes, and comments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/posts", tags=["Comments"])

@app.get("/")
async def root():
    return {"message": "Welcome to LawVriksh Blog Management System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
