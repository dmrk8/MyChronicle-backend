from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.shared.base import CamelModel


class Rating(BaseModel):
    Source: str
    Value: str


class OMDbData(CamelModel):
    Title: str
    Year: str
    Rated: Optional[str] = None
    Released: Optional[str] = None
    Runtime: Optional[str] = None
    Genre: Optional[str] = None
    Director: Optional[str] = None
    Writer: Optional[str] = None
    Actors: Optional[str] = None
    Plot: Optional[str] = None
    Language: Optional[str] = None
    Country: Optional[str] = None
    Awards: Optional[str] = None
    Poster: Optional[str] = None
    Ratings: Optional[List[Rating]] = None
    Metascore: Optional[str] = None
    imdb_rating: Optional[str] = None
    imdb_votes: Optional[str] = None
    imdbID: str
    Type: str
    DVD: Optional[str] = None
    BoxOffice: Optional[str] = None
    Production: Optional[str] = None
    Website: Optional[str] = None
    total_seasons: Optional[str] = None
    Response: str
