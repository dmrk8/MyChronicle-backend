from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class TMDB_Search_Movie(BaseModel):
    backdrop_path: Optional[str] = Field(alias="backdropPath")
    genre_ids: List[int] = Field(alias="genreIds")
    id: int
    original_language: str = Field(alias="originalLanguage")
    original_title: str = Field(alias="originalTitle")
    overview: str
    poster_path: Optional[str] = Field(alias="posterPath")
    release_date: str = Field(alias="releaseDate")
    title: str
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
class TMDB_Genre(BaseModel):
    id: int
    name: str
    
class TMDB_MovieDetail(BaseModel):
    backdrop_path: Optional[str] = Field(alias="backdropPath")
    collection_id: int = Field(alias="collectionId")
    budget: int
    genres: List[TMDB_Genre]
    id: int
    imdb_id: Optional[str] = Field(alias="imdbId")
    origin_country: List[str] = Field(alias="originCountry")
    original_language: str = Field(alias="originalLanguage")
    original_title: str = Field(alias="originalTitle")
    overview: str
    poster_path: Optional[str] = Field(alias="posterPath")
    release_date: str = Field(alias="releaseDate")
    runtime: int
    status: str
    title: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
    
class TMDBPagination(BaseModel):
    results: List
    page: int
    total_pages: int = Field(..., serialization_alias="totalPages")
    total_results: int = Field(..., serialization_alias="totalResults")
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    
