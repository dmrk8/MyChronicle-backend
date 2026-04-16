from pydantic import BaseModel
from app.models.media_models import AnimeDetailed, MangaDetailed, MediaPagination

class CachedAnimeDetail(BaseModel):
    data: AnimeDetailed

class CachedMangaDetail(BaseModel):
    data: MangaDetailed
    
class CachedMediaPagination(BaseModel):
    data: MediaPagination