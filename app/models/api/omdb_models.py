from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class Rating(BaseModel):
    Source: str
    Value: str


class OMDbData(BaseModel):
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
    imdb_rating: Optional[str] = Field(None, alias="imdbRating")
    imdb_votes: Optional[str] = Field(None, alias="imdbVotes")
    imdbID: str
    Type: str
    DVD: Optional[str]
    BoxOffice: Optional[str]
    Production: Optional[str]
    Website: Optional[str]
    total_seasons: Optional[str] = Field(None, alias="totalSeasons")
    Response: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
