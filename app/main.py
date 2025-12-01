from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.search_router import search_router
from app.routes.auth_router import auth_router
from app.routes.user_router import user_router
from app.routes.review_router import review_router
from app.routes.discover_router import discover_router
from app.routes.media_router import media_router
from app.routes.imdb_router import imdb_router

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

app.include_router(search_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(review_router)
app.include_router(discover_router)
app.include_router(media_router)
app.include_router(imdb_router)

@app.get("/")
async def root(q : str):
    return {"msg": "root is running"}

