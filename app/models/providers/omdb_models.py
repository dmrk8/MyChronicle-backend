from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.shared.base import CamelModel


class Rating(BaseModel):
    Source: str
    Value: str


class OMDbData(CamelModel):
    Title: str
    Year: str
    Rated: Optional[str]
    Released: Optional[str]
    Runtime: Optional[str]
    Genre: Optional[str]
    Director: Optional[str]
    Writer: Optional[str]
    Actors: Optional[str]
    Plot: Optional[str]
    Language: Optional[str]
    Country: Optional[str]
    Awards: Optional[str]
    Poster: Optional[str]
    Ratings: Optional[List[Rating]]
    Metascore: Optional[str]
    imdb_rating: Optional[str]  
    imdb_votes: Optional[str] 
    imdbID: str
    Type: str
    DVD: Optional[str] = None
    BoxOffice: Optional[str] = None
    Production: Optional[str] = None
    Website: Optional[str] = None
    total_seasons: Optional[str] 
    Response: str
