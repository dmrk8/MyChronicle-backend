import json
from pathlib import Path
from typing import Dict, Optional

MOVIE_GENRES_FILE = Path(__file__).parent.parent / "data" / "tmdb_movie_genres.json"
TV_GENRES_FILE = Path(__file__).parent.parent / "data" / "tmdb_tv_genres.json"

_movie_genres_cache: Optional[Dict[int, str]] = None
_tv_genres_cache: Optional[Dict[int, str]] = None


def _load_movie_genres_cache() -> Dict[int, str]:
    global _movie_genres_cache
    if _movie_genres_cache is None:
        try:
            with open(MOVIE_GENRES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            _movie_genres_cache = {g["id"]: g["name"] for g in data.get("genres", [])}
        except (FileNotFoundError, json.JSONDecodeError):
            _movie_genres_cache = {}
    return _movie_genres_cache


def _load_tv_genres_cache() -> Dict[int, str]:
    global _tv_genres_cache
    if _tv_genres_cache is None:
        try:
            with open(TV_GENRES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            _tv_genres_cache = {g["id"]: g["name"] for g in data.get("genres", [])}
        except (FileNotFoundError, json.JSONDecodeError):
            _tv_genres_cache = {}
    return _tv_genres_cache


def get_movie_genre_name_by_id(genre_id: int) -> Optional[str]:
    """Get movie genre name by ID."""
    cache = _load_movie_genres_cache()
    return cache.get(genre_id)


def get_tv_genre_name_by_id(genre_id: int) -> Optional[str]:
    """Get TV genre name by ID."""
    cache = _load_tv_genres_cache()
    return cache.get(genre_id)


