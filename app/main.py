from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exception_handlers import app_exception_handler, unhandled_exception_handler
from app.core.exceptions import AppException
from app.middleware.request_context import request_context_middleware
import structlog

from app.core.infrastructure import lifespan
from app.core.config import get_settings


from app.routes.auth_router import auth_router
from app.routes.user_router import user_router

from app.routes.imdb_router import imdb_router
from app.routes.igdb_router import igdb_router
from app.routes.anilist_router import anilist_router
from app.routes.tmdb_router import tmdb_router
from app.routes.user_media_entry_router import user_media_entry_router

log = structlog.get_logger()

app = FastAPI(title=get_settings().service_name, lifespan=lifespan)


app.middleware("http")(request_context_middleware)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/health")
async def health_check():
    log.info("health check")
    return {
        "status": "healthy",
        "service": get_settings().service_name,
        "environment": get_settings().env,
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(imdb_router)
app.include_router(igdb_router)
app.include_router(anilist_router)
app.include_router(tmdb_router)
app.include_router(user_media_entry_router)

@app.get("/")
async def root(q: str):
    return {"msg": "root is running"}
