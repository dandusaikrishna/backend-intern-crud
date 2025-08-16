# LawVriksh Blog Management System

A FastAPI-based blog management system with CRUD operations, authentication, likes, and comments functionality.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Blog Post CRUD**: Create, read, update, and delete blog posts
- **Like System**: Users can like/unlike posts (one like per user per post)
- **Comment System**: Users can add comments and view comments on posts
- **Protected Routes**: All write operations require authentication

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/backend-intern-crud.git
cd backend-intern-crud
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables (optional):
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///./blog.db"
```

### Running the Application

1. Start the FastAPI server:
```bash
uvicorn src.main:app --reload --port 8000
```

2. Access the application:
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user (returns JWT token)

### Blog Posts
- `GET /api/posts/` - Get all blog posts
- `GET /api/posts/{id}` - Get a single blog post
- `POST /api/posts/` - Create a new blog post (requires auth)
- `PUT /api/posts/{id}` - Update a blog post (requires auth, author only)
- `DELETE /api/posts/{id}` - Delete a blog post (requires auth, author only)

### Likes
- `POST /api/posts/{id}/like` - Like/unlike a blog post (requires auth)

### Comments
- `POST /api/posts/{id}/comment` - Add comment to a blog post (requires auth)
- `GET /api/posts/{id}/comments` - Get all comments for a blog post

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Database Schema

The system uses SQLite by default with the following models:
- **Users**: User authentication and profile data
- **BlogPosts**: Blog post content and metadata
- **Likes**: User likes on posts (unique constraint per user-post)
- **Comments**: User comments on posts

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (for deletions)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
