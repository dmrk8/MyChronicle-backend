from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.request_context import request_context_middleware
import structlog

from app.core.infrastructure import lifespan
from app.core.config import get_settings


from app.routes.auth_router import auth_router
from app.routes.user_router import user_router

from app.routes.review_router import review_router
from app.routes.imdb_router import imdb_router
from app.routes.igdb_router import igdb_router
from app.routes.anilist_router import anilist_router
from app.routes.tmdb_router import tmdb_router
from app.routes.user_media_entry_router import user_media_entry_router

log = structlog.get_logger()

app = FastAPI(title=get_settings().service_name, lifespan=lifespan)


app.middleware("http")(request_context_middleware)


@app.get("/health")
async def health_check():
    log.info("health check")
    return {
        "status": "healthy",
        "service": get_settings().service_name,
        "environment": get_settings().env,
    }


origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(review_router)
app.include_router(imdb_router)
app.include_router(igdb_router)
app.include_router(anilist_router)
app.include_router(tmdb_router)
app.include_router(user_media_entry_router)

@app.get("/")
async def root(q: str):
    return {"msg": "root is running"}
