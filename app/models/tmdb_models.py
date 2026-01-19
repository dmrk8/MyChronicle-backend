from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class TMDBGenre(BaseModel):
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBProductionCompany(BaseModel):
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBSpokenLanguage(BaseModel):
    english_name: str = Field(..., alias="englishName")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBBelongsToCollection(BaseModel):
    id: int
    name: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCreatedBy(BaseModel):
    name: str
    original_name: str = Field(..., alias="originalName")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBLastEpisodeToAir(BaseModel):
    name: str
    overview: str
    vote_average: float = Field(..., alias="voteAverage")
    air_date: str = Field(..., alias="airDate")
    episode_number: int = Field(..., alias="episodeNumber")
    episode_type: str = Field(..., alias="episodeType")
    runtime: Optional[int]
    season_number: int = Field(..., alias="seasonNumber")
    still_path: Optional[str] = Field(None, alias="stillPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class TMDBNextEpisodeToAir(BaseModel):
    air_date: str = Field(..., alias="airDate")
    episode_number: int = Field(..., alias="episodeNumber")
    season_number: int = Field(..., alias="seasonNumber")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
class TMDBNetwork(BaseModel):
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBSeason(BaseModel):
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_count: int = Field(..., alias="episodeCount")
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    season_number: int = Field(..., alias="seasonNumber")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBKeyword(BaseModel):
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBTvKeywords(BaseModel):
    results: List[TMDBKeyword]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMovieKeywords(BaseModel):
    keywords: List[TMDBKeyword]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBExternalIds(BaseModel):
    imdb_id: Optional[str] = Field(None, alias="imdbId")
    freebase_mid: Optional[str] = None
    freebase_id: Optional[str] = None
    tvdb_id: Optional[int] = None
    tvrage_id: Optional[int] = None
    wikidata_id: Optional[str] = None
    facebook_id: Optional[str] = None
    instagram_id: Optional[str] = None
    twitter_id: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCollectionPart(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    id: int
    title: str
    original_title: str = Field(..., alias="originalTitle")
    media_type: str = Field(..., alias="mediaType")
    release_date: str = Field(..., alias="releaseDate")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCollection(BaseModel):
    id: int
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    parts: List[TMDBCollectionPart]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMediaMinimal(BaseModel):
    adult: bool
    poster_path: Optional[str] = Field(None, alias="posterPath")
    genre_ids: List[int] = Field(..., alias="genreIds")
    id: int
    original_language: str = Field(..., alias="originalLanguage")
    popularity: float
    media_type: Optional[str] = Field(None, alias="mediaType")
    vote_average: float = Field(..., alias="voteAverage")

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


class TMDBMediaMinimalRecommendation(BaseModel):
    poster_path: Optional[str] = Field(None, alias="posterPath")
    id: int

    title: Optional[str] = None
    original_title: Optional[str] = Field(None, alias="originalTitle")

    # TV-specific fields
    name: Optional[str] = None
    original_name: Optional[str] = Field(None, alias="originalName")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBPaginationRecommendation(BaseModel):
    results: List[TMDBMediaMinimalRecommendation]
    page: int
    total_pages: int = Field(..., alias="totalPages")
    total_results: int = Field(..., alias="totalResults")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBAlternativeTitle(BaseModel):
    title: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBAlternativeTitles(BaseModel):
    titles: List[TMDBAlternativeTitle]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBAlternativeTitlesTv(BaseModel):
    results: List[TMDBAlternativeTitle]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCast(BaseModel):
    name: str
    character: Optional[str] = None
    order: Optional[int] = None
    known_for_department: Optional[str] = Field(None, alias="knownForDepartment")
    original_name: Optional[str] = Field(None, alias="originalName")
    profile_path: Optional[str] = Field(None, alias="profilePath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCredits(BaseModel):
    cast: List[TMDBCast]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMediaDetailBase(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    genres: List[TMDBGenre]
    id: int
    imdb_id: Optional[str] = Field(None, alias="imdbId")
    origin_country: List[str] = Field(..., alias="originCountry")
    original_language: str = Field(..., alias="originalLanguage")
    overview: str
    popularity: float
    poster_path: Optional[str] = Field(None, alias="posterPath")
    production_companies: List[TMDBProductionCompany] = Field(
        ..., alias="productionCompanies"
    )
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
    recommendations: Optional[TMDBPaginationRecommendation] = None
    alternative_titles: Optional[TMDBAlternativeTitles] = Field(
        None, alias="alternativeTitles"
    )
    credits: Optional[TMDBCredits] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBProductionCountry(BaseModel):
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBTVDetail(TMDBMediaDetailBase):
    created_by: Optional[List[TMDBCreatedBy]] = Field(None, alias="createdBy")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    in_production: Optional[bool] = Field(None, alias="inProduction")
    languages: Optional[List[str]] = None
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")
    last_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(
        None, alias="lastEpisodeToAir"
    )
    name: Optional[str] = None
    next_episode_to_air: Optional[TMDBNextEpisodeToAir] = Field(
        None, alias="nextEpisodeToAir"
    )
    networks: Optional[List[TMDBNetwork]] = None
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    original_name: Optional[str] = Field(None, alias="originalName")
    seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None
    keywords: Optional[TMDBTvKeywords] = None
    credits: Optional[TMDBCredits] = None
    recommendations: Optional[TMDBPaginationRecommendation] = None
    production_countries: Optional[List[TMDBProductionCountry]] = Field(
        None, alias="productionCountries"
    )
    alternative_titles: Optional[TMDBAlternativeTitlesTv] = Field(
        None, alias="alternativeTitles"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
