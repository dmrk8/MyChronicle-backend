
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
    name: Optional[str] = Field(None, alias="name")
    overview: Optional[str] = Field(None, alias="overview")
    vote_average: Optional[float] = Field(None, alias="voteAverage")
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_number: Optional[int] = Field(None, alias="episodeNumber")
    episode_type: Optional[str] = Field(None, alias="episodeType")
    runtime: Optional[int] = Field(None, alias="runtime")
    season_number: Optional[int] = Field(None, alias="seasonNumber")
    still_path: Optional[str] = Field(None, alias="stillPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBNextEpisodeToAir(BaseModel):
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_number: Optional[int] = Field(None, alias="episodeNumber")
    season_number: Optional[int] = Field(None, alias="seasonNumber")

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
    poster_path: Optional[str] = Field(None, alias="posterPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBCollection(BaseModel):
    id: int
    name: str
    overview: Optional[str] = Field(None, alias="overview")
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    parts: Optional[List[TMDBCollectionPart]] = Field(None)

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMediaMinimal(BaseModel):
    adult: bool
    poster_path: Optional[str] = Field(None, alias="posterPath")
    genre_ids: List[int] = Field(..., alias="genreIds")
    id: int
    original_language: Optional[str] = Field(None, alias="originalLanguage")
    popularity: Optional[float] = Field(None, alias="popularity")
    media_type: Optional[str] = Field(None, alias="mediaType")
    vote_average: Optional[float] = Field(None, alias="voteAverage")

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
    total_pages: int = Field(...)
    total_results: int = Field(...)

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMediaMinimalRecommendation(BaseModel):
    poster_path: Optional[str] = Field(None, alias="posterPath")
    id: int
    media_type: str = Field(alias="mediaType")
    genre_ids: List[int] = Field(..., alias="genreIds")
    original_language: str = Field(..., alias="originalLanguage")

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


class TMDBVideo(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    site: Optional[str] = None
    type: Optional[str] = None
    official: Optional[bool] = None


class TMDBVideos(BaseModel):
    id: int
    results: List[TMDBVideo]


class TMDBProductionCountry(BaseModel):
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMediaDetailBase(BaseModel):
    # --- Identifiers ---
    id: int
    media_type: Optional[str] = Field(None, alias="mediaType")

    # --- Content Flags ---
    adult: bool
    status: Optional[str] = Field(None, alias="status")

    # --- Titles & Description ---
    overview: Optional[str] = Field(None, alias="overview")
    tagline: Optional[str] = None

    # --- Media Details ---
    genres: Optional[List[TMDBGenre]] = Field(None, alias="genres")
    original_language: Optional[str] = Field(None, alias="originalLanguage")
    origin_country: Optional[List[str]] = Field(None, alias="originCountry")

    # --- Media Assets ---
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")

    # --- Production ---
    production_companies: Optional[List[TMDBProductionCompany]] = Field(
        None, alias="productionCompanies"
    )
    spoken_languages: Optional[List[TMDBSpokenLanguage]] = Field(
        None, alias="spokenLanguages"
    )

    # --- Metrics ---
    popularity: Optional[float] = Field(None, alias="popularity")
    vote_average: Optional[float] = Field(None, alias="voteAverage")
    vote_count: Optional[int] = Field(None, alias="voteCount")
    
    videos : Optional[TMDBVideos] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBMovieDetail(TMDBMediaDetailBase):
    # --- External IDs ---
    imdb_id: Optional[str] = Field(None, alias="imdbId")

    # --- Titles ---
    title: Optional[str] = None
    original_title: Optional[str] = Field(None, alias="originalTitle")

    # --- Dates ---
    release_date: Optional[str] = Field(None, alias="releaseDate")

    # --- Content ---
    runtime: Optional[int] = None

    # --- Financials ---
    budget: Optional[int] = None
    revenue: Optional[int] = None

    # --- Collections ---
    belongs_to_collection: Optional[TMDBBelongsToCollection] = Field(
        None, alias="belongsToCollection"
    )

    # --- Metadata ---
    keywords: Optional[TMDBMovieKeywords] = None
    alternative_titles: Optional[TMDBAlternativeTitles] = Field(
        None, alias="alternativeTitles"
    )

    # --- Credits & Recommendations ---
    credits: Optional[TMDBCredits] = None
    recommendations: Optional[TMDBPaginationRecommendation] = None

class TMDBTVDetail(TMDBMediaDetailBase):
    # --- Titles ---
    name: Optional[str] = None
    original_name: Optional[str] = Field(None, alias="originalName")

    # --- Dates ---
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")

    # --- Content Structure ---
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None

    # --- Airing Info ---
    next_episode_to_air: Optional[TMDBNextEpisodeToAir] = Field(
        None, alias="nextEpisodeToAir"
    )
    last_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(
        None, alias="lastEpisodeToAir"
    )
    in_production: Optional[bool] = Field(None, alias="inProduction")

    # --- Production ---
    created_by: Optional[List[TMDBCreatedBy]] = Field(None, alias="createdBy")
    networks: Optional[List[TMDBNetwork]] = None
    production_countries: Optional[List[TMDBProductionCountry]] = Field(
        None, alias="productionCountries"
    )
    languages: Optional[List[str]] = None

    # --- External IDs ---
    external_ids: Optional[TMDBExternalIds] = Field(None, alias="externalIds")

    # --- Metadata ---
    keywords: Optional[TMDBTvKeywords] = None
    alternative_titles: Optional[TMDBAlternativeTitlesTv] = Field(
        None, alias="alternativeTitles"
    )

    # --- Credits & Recommendations ---
    credits: Optional[TMDBCredits] = None
    recommendations: Optional[TMDBPaginationRecommendation] = None

