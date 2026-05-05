from pydantic import BaseModel
from app.models.api.media_response import (
    AnimeDetailed,
    MangaDetailed,
    MediaPagination,
    MovieDetailedWithCollection,
    TVDetailed,
)


class CachedAnimeDetail(BaseModel):
    data: AnimeDetailed


class CachedMangaDetail(BaseModel):
    data: MangaDetailed


class CachedMovieDetailWithCollection(BaseModel):
    data: MovieDetailedWithCollection


class CachedTVDetail(BaseModel):
    data: TVDetailed


class CachedMediaPagination(BaseModel):
    data: MediaPagination
