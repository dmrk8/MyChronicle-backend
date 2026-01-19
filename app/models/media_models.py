from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union

from app.models.anilist_models import (
    Characters,
    CoverImage,
    MediaDate,
    NextAiringEpisode,
    Recommendations,
    Relations,
    Studios,
    Tag,
    Title,
)
from app.models.tmdb_models import (
    TMDBAlternativeTitles,
    TMDBBelongsToCollection,
    TMDBCollectionPart,
    TMDBCreatedBy,
    TMDBCredits,
    TMDBLastEpisodeToAir,
    TMDBMovieKeywords,
    TMDBNextEpisodeToAir,
    TMDBPagination,
    TMDBPaginationRecommendation,
    TMDBProductionCompany,
    TMDBSeason,
    TMDBSpokenLanguage,
    TMDBExternalIds,
    TMDBNetwork,
    TMDBTvKeywords,
    TMDBProductionCountry,
)


class MediaMinimal(BaseModel):
    id: int
    external_source: str = Field(alias="externalSource")
    media_type: str = Field(alias="mediaType")

    # shared
    title: str
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    average_score: Optional[float] = Field(None, alias="averageScore")
    banner_image: Optional[str] = Field(None, alias="bannerImage")

    # anime
    episodes: Optional[int] = None
    main_studio: Optional[str] = Field(None, alias="mainStudio")

    # manga
    chapters: Optional[int] = None

    # movie
    release_date: Optional[str] = Field(None, alias="releaseDate")

    # tv
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaPagination(BaseModel):
    results: List[MediaMinimal]
    current_page: int = Field(..., alias="currentPage")
    per_page: Optional[int] = Field(None, alias="perPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
    total: Optional[int] = None

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)


class MediaBase(BaseModel):
    id: int
    external_source: str = Field(alias="externalSource")
    media_type: str = Field(alias="mediaType")
    title: str
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    average_score: Optional[float] = Field(None, alias="averageScore")
    description: Optional[str] = None
    banner_image: Optional[str] = Field(None, alias="bannerImage")
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    synonyms: Optional[List[str]] = None

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
    )


class MediaStudios(BaseModel):
    is_main: bool = Field(..., alias="isMain")
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaRelations(BaseModel):
    relation_type: str = Field(..., alias="relationType")
    id: int
    title: str
    format: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaRecommendation(BaseModel):
    id: int
    title: str
    cover_image: Optional[str] = Field(None, alias="coverImage")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaCharacters(BaseModel):
    role: str
    image: str
    name: str


class AnimeDetailed(MediaBase):
    episodes: Optional[int] = None
    studios: Optional[List[MediaStudios]] = None
    duration: Optional[int] = None
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    start_date: Optional[MediaDate] = Field(None, alias="startDate")
    end_date: Optional[MediaDate] = Field(None, alias="endDate")
    next_airing_episode: Optional[NextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    source: Optional[str] = None
    tags: Optional[List[Tag]] = None
    relations: Optional[List[MediaRelations]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    characters: Optional[List[MediaCharacters]] = None


class MangaDetailed(MediaBase):
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    start_date: Optional[MediaDate] = Field(None, alias="startDate")
    end_date: Optional[MediaDate] = Field(None, alias="endDate")
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    source: Optional[str] = None
    tags: Optional[List[Tag]] = None
    relations: Optional[List[MediaRelations]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    characters: Optional[List[MediaCharacters]] = None

class MediaCast(BaseModel):
    name: str
    character: Optional[str] = None
    cast_image: Optional[str]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MovieDetailed(MediaBase):
    release_date: Optional[str] = Field(None, alias="releaseDate")
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    origin_country: List[str] = Field(..., alias="originCountry")
    original_language: Optional[str] = Field(None, alias="originalLanguage")
    belongs_to_collection: Optional[TMDBBelongsToCollection] = Field(
        None, alias="belongsToCollection"
    )
    production_companies: Optional[List[str]] = Field(
        None, alias="productionCompanies"
    )
    keywords: Optional[List[str]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    alternative_titles: Optional[Optional[List[str]]] = Field(
        None, alias="alternativeTitles"
    )
    credits: Optional[List[MediaCast]] = None
    spoken_languages: Optional[List[str]] = Field(None, alias="spokenLanguages")


class TVDetailed(MediaBase):
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")
    created_by: Optional[List[str]] = Field(None, alias="createdBy")
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    next_episode_to_air: Optional[TMDBNextEpisodeToAir] = Field(
        None, alias="nextEpisodeToAir"
    )
    seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None  # e.g., Scripted, Documentary
    original_language: Optional[str] = Field(None, alias="originalLanguage")
    in_production: Optional[bool] = Field(None, alias="inProduction")
    languages: Optional[List[str]] = None
    last_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(
        None, alias="lastEpisodeToAir"
    )
    networks: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    credits: Optional[List[MediaCast]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    production_countries: Optional[List[str]] = Field(
        None, alias="productionCountries"
    )


MediaDetailedUnion = Union[AnimeDetailed, MangaDetailed, MovieDetailed, TVDetailed]


class MovieCollection(BaseModel):
    id: int
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    parts: List[TMDBCollectionPart]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaDetailed(BaseModel):
    id: int
    external_source: str = Field(alias="externalSource")
    media_type: str = Field(alias="mediaType")

    # shared
    title: str
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    average_score: Optional[float] = Field(None, alias="averageScore")
    description: Optional[str] = None
    banner_image: Optional[str] = Field(None, alias="bannerImage")
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    synonyms: Optional[List[str]] = None
    # tags: List[Tag] = []

    # anime
    episodes: Optional[int] = None
    # main_studio: Optional[str] = Field(None, alias="mainStudio")
    studios: Optional[List[str]] = None
    duration: Optional[int] = None
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    next_airing_episode: Optional[str] = Field(None, alias="nextAiringEpisode")
    # relations: Relations = Relations(edges=[])

    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    source: Optional[str] = None
    synonyms: Optional[List[str]] = None

    # manga
    chapters: Optional[int] = None
    volumes: Optional[int] = None

    # imdb_id: Optional[str] = Field(None, alias="imdbId")
    original_language: Optional[str] = Field(None, alias="originalLanguage")

    # movie
    release_date: Optional[str] = Field(None, alias="releaseDate")
    # belongs_to_collection: Optional[TMDBBelongsToCollection] = Field(
    #    None, alias="belongsToCollection"
    # )
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None

    # tv
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    created_by: Optional[str] = Field(None, alias="createdBy")
    episode_run_time: Optional[int] = Field(None, alias="episodeRunTime")
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")
    # next_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(None, alias="nextEpisodeToAir")
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    # seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaFeaturedBulk(BaseModel):
    trending: Optional[List[MediaMinimal]] = None
    popular_season: Optional[List[MediaMinimal]] = Field(
        default=None, alias="popularSeason"
    )
    upcoming: Optional[List[MediaMinimal]] = None
    all_time: Optional[List[MediaMinimal]] = Field(default=None, alias="allTime")
    all_time_manhwa: Optional[List[MediaMinimal]] = Field(
        default=None, alias="allTimeManhwa"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
