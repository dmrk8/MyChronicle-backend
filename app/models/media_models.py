from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

from app.enums.user_media_entry_enums import MediaType
from app.models.anilist_models import (
    NextAiringEpisode,
    Tag,
)
from app.models.tmdb_models import (
    TMDBLastEpisodeToAir,
    TMDBNextEpisodeToAir,
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
    media_type: MediaType = Field(alias="mediaType")
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


class MediaStudio(BaseModel):
    is_main: bool = Field(..., alias="isMain")
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaRelation(BaseModel):
    relation_type: Optional[str] = Field(None, alias="relationType")
    id: int
    title: str
    format: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    media_type: MediaType = Field(alias="mediaType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaRecommendation(BaseModel):
    id: int
    title: str
    cover_image: Optional[str] = Field(None, alias="coverImage")
    media_type: MediaType = Field(alias="mediaType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaVoiceActor(BaseModel):
    image: str
    name: str


class MediaCharacter(BaseModel):
    role: str
    image: str
    name: str
    voice_actor: Optional[MediaVoiceActor] = Field(None, alias="voiceActor")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AnimeDetailed(MediaBase):
    episodes: Optional[int] = None
    studios: Optional[List[MediaStudio]] = None
    duration: Optional[int] = None
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    next_airing_episode: Optional[NextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    source: Optional[str] = None
    tags: Optional[List[Tag]] = None
    relations: Optional[List[MediaRelation]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    characters: Optional[List[MediaCharacter]] = None


class MangaDetailed(MediaBase):
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    source: Optional[str] = None
    tags: Optional[List[Tag]] = None
    relations: Optional[List[MediaRelation]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    characters: Optional[List[MediaCharacter]] = None


class MediaCast(BaseModel):
    name: str
    character: Optional[str] = None
    cast_image: Optional[str] = Field(None, alias="castImage")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaBelongsToCollection(BaseModel):
    id: int
    name: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MovieDetailed(MediaBase):
    release_date: Optional[str] = Field(None, alias="releaseDate")
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    origin_country: List[str] = Field(..., alias="originCountry")
    original_language: Optional[str] = Field(None, alias="originalLanguage")
    belongs_to_collection: Optional[MediaBelongsToCollection] = Field(
        None, alias="belongsToCollection"
    )
    production_companies: Optional[List[str]] = Field(None, alias="productionCompanies")
    keywords: Optional[List[str]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    alternative_titles: Optional[Optional[List[str]]] = Field(
        None, alias="alternativeTitles"
    )
    credits: Optional[List[MediaCast]] = None
    spoken_languages: Optional[List[str]] = Field(None, alias="spokenLanguages")


class MediaSeason(BaseModel):
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_count: int = Field(..., alias="episodeCount")
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    season_number: int = Field(..., alias="seasonNumber")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TVDetailed(MediaBase):
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")
    created_by: Optional[List[str]] = Field(None, alias="createdBy")
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    next_episode_to_air: Optional[TMDBNextEpisodeToAir] = Field(
        None, alias="nextEpisodeToAir"
    )
    seasons: Optional[List[MediaSeason]] = None
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
    production_countries: Optional[List[str]] = Field(None, alias="productionCountries")

class MovieCollectionPart(BaseModel):
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    id: int
    title: str
    media_type: MediaType = Field(..., alias="mediaType")
    release_date: str = Field(..., alias="releaseDate")
    poster_path: Optional[str] = Field(None, alias="posterPath")  


    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class MovieCollection(BaseModel):
    id: int
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    parts: List[MovieCollectionPart]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


