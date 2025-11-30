from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class TMDBGenre(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBProductionCompany(BaseModel):
    id: int
    logo_path: Optional[str] = Field(None, alias="logoPath")
    name: str
    origin_country: str = Field(..., alias="originCountry")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBSpokenLanguage(BaseModel):
    english_name: str = Field(..., alias="englishName")
    iso_639_1: str = Field(..., alias="iso6391")
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBBelongsToCollection(BaseModel):
    id: int
    name: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCreatedBy(BaseModel):
    id: int
    credit_id: str = Field(..., alias="creditId")
    name: str
    original_name: str = Field(..., alias="originalName")
    gender: int
    profile_path: Optional[str] = Field(None, alias="profilePath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBLastEpisodeToAir(BaseModel):
    id: int
    name: str
    overview: str
    vote_average: float = Field(..., alias="voteAverage")
    vote_count: int = Field(..., alias="voteCount")
    air_date: str = Field(..., alias="airDate")
    episode_number: int = Field(..., alias="episodeNumber")
    episode_type: str = Field(..., alias="episodeType")
    production_code: str = Field(..., alias="productionCode")
    runtime: int
    season_number: int = Field(..., alias="seasonNumber")
    show_id: int = Field(..., alias="showId")
    still_path: Optional[str] = Field(None, alias="stillPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBNetwork(BaseModel):
    id: int
    logo_path: Optional[str] = Field(None, alias="logoPath")
    name: str
    origin_country: str = Field(..., alias="originCountry")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBSeason(BaseModel):
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_count: int = Field(..., alias="episodeCount")
    id: int
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    season_number: int = Field(..., alias="seasonNumber")
    vote_average: float = Field(..., alias="voteAverage")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBKeyword(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBTvKeywords(BaseModel):
    results: List[TMDBKeyword]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMovieKeywords(BaseModel):
    keywords: List[TMDBKeyword]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class TMDBMediaMinimal(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    genre_ids : List[int] = Field(..., alias="genreIds")
    id: int
    original_language: str = Field(..., alias="originalLanguage")
    popularity: float
    media_type: Optional[str] = Field(None, alias="mediaType")
    vote_average: float = Field(..., alias="voteAverage")
    imdb_rating_value: Optional[float] = None

    # Movie-specific fields
    title: Optional[str] = None
    original_title: Optional[str] = Field(None, alias="originalTitle")
    release_date: Optional[str] = Field(None, alias="releaseDate")

    # TV-specific fields
    name: Optional[str] = None
    original_name: Optional[str] = Field(None, alias="originalName")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    origin_country: Optional[List[str]] = Field(None, alias="originCountry")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBPageInfo(BaseModel):
    page: int
    total_pages: int = Field(..., alias="totalPages")
    total_results: int = Field(..., alias="totalResults")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBPagination(BaseModel):
    results: List[TMDBMediaMinimal]
    page: int
    total_pages: int = Field(..., alias="totalPages")
    total_results: int = Field(..., alias="totalResults")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMediaDetailBase(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    genres: List[TMDBGenre]
    id: int
    imdb_id: Optional[str] = Field(None, alias="imdbId")
    imdb_rating_count: Optional[int] = None
    imdb_rating_value: Optional[float] = None
    origin_country: List[str] = Field(..., alias="originCountry")
    original_language: str = Field(..., alias="originalLanguage")
    overview: str
    popularity: float
    poster_path: Optional[str] = Field(None, alias="posterPath")
    production_companies: List[TMDBProductionCompany] = Field(..., alias="productionCompanies")
    spoken_languages: List[TMDBSpokenLanguage] = Field(..., alias="spokenLanguages")
    status: str
    tagline: Optional[str] = None
    vote_average: float = Field(..., alias="voteAverage")
    vote_count: Optional[int] = Field(None, alias="voteCount")
    media_type: Optional[str] = Field(None, alias="mediaType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMovieDetail(TMDBMediaDetailBase):
    belongs_to_collection: Optional[TMDBBelongsToCollection] = Field(
        None, alias="belongsToCollection"
    )
    budget: Optional[int] = None
    original_title: Optional[str] = Field(None, alias="originalTitle")
    release_date: Optional[str] = Field(None, alias="releaseDate")
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    title: Optional[str] = None
    keywords: Optional[TMDBMovieKeywords] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBTVDetail(TMDBMediaDetailBase):
    created_by: Optional[List[TMDBCreatedBy]] = Field(None, alias="createdBy")
    episode_run_time: Optional[List[int]] = Field(None, alias="episodeRunTime")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    in_production: Optional[bool] = Field(None, alias="inProduction")
    languages: Optional[List[str]] = None
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")
    last_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(None, alias="lastEpisodeToAir")
    name: Optional[str] = None
    next_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(None, alias="nextEpisodeToAir")
    networks: Optional[List[TMDBNetwork]] = None
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    original_name: Optional[str] = Field(None, alias="originalName")
    seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None
    keywords: Optional[TMDBTvKeywords] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
