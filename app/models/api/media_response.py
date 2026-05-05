from token import OP

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

from app.enums.media_enums import MediaType

from app.models.shared.media import MediaTag, MediaTitle, MediaScore


class TMDBMediaLastEpisodeToAir(BaseModel):
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


class TMDBMediaNextAiringEpisode(BaseModel):
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_number: Optional[int] = Field(None, alias="episodeNumber")
    season_number: Optional[int] = Field(None, alias="seasonNumber")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AniMediaNextAiringEpisode(BaseModel):
    episode: Optional[int] = None
    airing_at: Optional[int] = Field(None, alias="airingAt")
    time_until_airing: Optional[int] = Field(None, alias="timeUntilAiring")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Trailer(BaseModel):
    url: Optional[str] = None
    thumbnail: Optional[str] = None


class MediaStudio(BaseModel):
    is_main: bool = Field(..., alias="isMain")
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaRelation(BaseModel):
    relation_type: Optional[str] = Field(None, alias="relationType")
    id: int
    title: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    media_type: MediaType = Field(alias="mediaType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaRecommendation(BaseModel):
    id: int
    title: Optional[str]
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


class MediaMinimal(BaseModel):
    id: int
    external_source: str = Field(alias="externalSource")
    media_type: MediaType = Field(alias="mediaType")

    # shared
    title: str = Field(description="Flattned title for display purposes")
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


class MediaSeason(BaseModel):
    air_date: Optional[str] = Field(None, alias="airDate")
    episode_count: int = Field(..., alias="episodeCount")
    name: str
    overview: str
    poster_path: Optional[str] = Field(None, alias="posterPath")
    season_number: int = Field(..., alias="seasonNumber")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MovieCollectionPart(BaseModel):
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    id: int
    title: str
    original_title: str = Field(..., alias="originalTitle")
    media_type: MediaType = Field(..., alias="mediaType")
    release_date: str = Field(..., alias="releaseDate")
    poster_path: Optional[str] = Field(None, alias="posterPath")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MovieCollection(BaseModel):
    id: int
    name: str
    overview: Optional[str] = None
    poster_path: Optional[str] = Field(None, alias="posterPath")
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    parts: List[MovieCollectionPart]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaBase(BaseModel):
    # --- Identifiers ---
    id: int
    external_source: str = Field(alias="externalSource")
    media_type: MediaType = Field(alias="mediaType")

    # --- Titles & Description ---
    title: Optional[MediaTitle] = None
    description: Optional[str] = None

    # --- Media Details ---
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    is_adult: Optional[bool] = Field(None, alias="isAdult")

    # --- Media Assets ---
    cover_image: Optional[str] = Field(None, alias="coverImage")
    banner_image: Optional[str] = Field(None, alias="bannerImage")
    trailer: Optional[Trailer] = None

    # --- Scores ---
    scores: Optional[List[MediaScore]] = None

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )


class AniMediaBase(MediaBase):
    # --- External IDs ---
    id_mal: Optional[int] = Field(None, alias="idMal")

    # --- Dates -------
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")

    # --- Production ---
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    source: Optional[str] = None
    
    synonyms: Optional[List[str]] = None
    
    # --- Metadata & Relations ---
    tags: Optional[List[MediaTag]] = None
    relations: Optional[List[MediaRelation]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    characters: Optional[List[MediaCharacter]] = None


class AnimeDetailed(AniMediaBase):
    # --- Content Structure ---
    episodes: Optional[int] = None
    duration: Optional[int] = None

    # --- Dates & Season ---
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")

    # --- Airing Info ---
    next_airing_episode: Optional[AniMediaNextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )

    # --- Production ---
    studios: Optional[List[MediaStudio]] = None


class MangaDetailed(AniMediaBase):
    # --- Content Structure ---
    chapters: Optional[int] = None
    volumes: Optional[int] = None


class TMDBMediaBase(MediaBase):
    original_language: Optional[str] = Field(None, alias="originalLanguage")

    # --- Metadata ---
    keywords: Optional[List[str]] = None
    credits: Optional[List[MediaCast]] = None
    recommendations: Optional[List[MediaRecommendation]] = None
    
    alternative_titles: Optional[List[str]] = Field(None, alias="alternativeTitles")

class TVDetailed(TMDBMediaBase):
    # --- Dates ---
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")

    # --- Content Structure ---
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")

    # --- Airing Info ---
    next_airing_episode: Optional[TMDBMediaNextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )
    last_episode_to_air: Optional[TMDBMediaLastEpisodeToAir] = Field(
        None, alias="lastEpisodeToAir"
    )

    # --- Production ---
    created_by: Optional[List[str]] = Field(None, alias="createdBy")
    networks: Optional[List[str]] = None
    production_countries: Optional[List[str]] = Field(None, alias="productionCountries")
    languages: Optional[List[str]] = None
    in_production: Optional[bool] = Field(None, alias="inProduction")

    # --- Structure ---
    seasons: Optional[List[MediaSeason]] = None
    type: Optional[str] = None  # Scripted, Documentary, etc.


class MovieDetailed(TMDBMediaBase):
    # --- Dates ---
    release_date: Optional[str] = Field(None, alias="releaseDate")

    # --- Financials ---
    budget: Optional[int] = None
    revenue: Optional[int] = None

    # --- Content ---
    runtime: Optional[int] = None

    # --- Production ---
    origin_country: Optional[List[str]] = Field(None, alias="originCountry")
    production_companies: Optional[List[str]] = Field(None, alias="productionCompanies")
    spoken_languages: Optional[List[str]] = Field(None, alias="spokenLanguages")

    # --- Collections ---
    belongs_to_collection: Optional[MediaBelongsToCollection] = Field(
        None, alias="belongsToCollection"
    )

    


class MovieDetailedWithCollection(MovieDetailed):
    collection: Optional[MovieCollection] = None
