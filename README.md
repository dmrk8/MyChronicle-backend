![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-brightgreen)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)

# MyChronicle — Backend

Backend API for **MyChronicle**, a media tracking application for anime, movies, TV shows.

This service retrieves media data from external APIs and stores user tracking data in MongoDB.

⚠️ This project is primarily intended for personal use due to rate limits imposed by third-party APIs.

## Frontend Repository

Frontend for this project:  
https://github.com/dmrk8/MyChronicle-frontend

## Features

- User registration, authentication & profile management
- JWT-based auth with HTTP-only cookie sessions (access + refresh tokens)
- Track media entries with status, ratings, and progress
- Write and manage media reviews
- Integration with multiple external media APIs
- Role-based access control (admin / user)

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.13 |
| Database | MongoDB (Motor async driver) |
| Cache | Redis |
| HTTP Client | HTTPX (async) |
| Deployment | Docker / Docker Compose |

## External API Integrations
| API | Purpose |
|---|---|
| [AniList](https://anilist.gitbook.io/anilist-apiv2-docs/) | Anime & Manga 
| [TMDB](https://developer.themoviedb.org/docs) | Movies & TV shows |

## Architecture

Client
   │
   ▼
FastAPI Backend
   │
   ├── MongoDB (user data)
   ├── Redis (cache)
   ├── AniList API
   └── TMDB API

## API Endpoints

| Prefix | Description |
|---|---|
| `/auth` | Login, logout, current user |
| `/users` | User CRUD |
| `/reviews` | Create, update, delete reviews |
| `/user-media-entries` | Track media entries |
| `/anilist` | Anime search & seasonal data |
| `/tmdb` | Movies & TV data |
| `/health` | Health check |

Interactive docs available at `/docs` (Swagger UI) when running.

## Environment Variables

Create a `.env` file in the project root:

```env
ENV=DEV
LOG_LEVEL=DEBUG
SERVICE_NAME=service_name

MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=database_name
REVIEW_COLLECTION=Reviews
USER_COLLECTION=Users
USER_MEDIA_ENTRY_COLLECTION=UserMediaEntries

JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS_DEFAULT=60
JWT_ISSUER=ISSUER
JWT_AUDIENCE=AUDIENCE

API_URL=http://localhost:8000

TMDB_API_KEY=your_tmdb_api_key
TMDB_ACCESS_TOKEN=your_tmdb_access_token

ALLOW_ORIGINS_STR=http://localhost:5173
SAMESITE=lax

```
## Installation & Running Locally

### Without Docker

```bash
# Clone the repo
git clone https://github.com/dmrk8/MyChronicle-backend.git
cd MyChronicle-backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create your .env file (see above)

# Run the server
uvicorn app.main:app --reload --port 8000
```

### With Docker

```bash
docker-compose up --build
```

The API will be available at:

```
http://localhost:8000
```

## Project Structure

```
app/
├── auth/           # JWT & session handling
├── context/        # Seasonal context helpers
├── core/           # Config, infrastructure, dependencies
├── enums/          # Enumerations for media types
├── extensions/     # Caching extensions (AniList)
├── integrations/   # External API clients
├── middleware/     # Request context middleware
├── models/         # Pydantic models
├── repositories/   # MongoDB data access layer
├── routes/         # FastAPI routers
├── services/       # Business logic layer
└── utils/          # Normalizers and helpers
```

## API Documentation

Once the server is running, interactive API documentation is available:

- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc

## License

This project is licensed under the MIT License.