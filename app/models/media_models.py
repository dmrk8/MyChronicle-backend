from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class MediaMinimal(BaseModel):

    id: int
    media_source: str = Field(alias="mediaSource")
    media_type: str = Field(alias="mediaType")

    # shared
    title: str
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    average_score: Optional[float] = Field(None, alias="averageScore")

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


class MediaDetailed(BaseModel):
    id: int
    media_source: str = Field(alias="mediaSource")
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
    #tags: List[Tag] = []
    
    # anime
    episodes: Optional[int] = None
    #main_studio: Optional[str] = Field(None, alias="mainStudio")
    studios: Optional[List[str]] = None 
    duration: Optional[int] = None
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    next_airing_episode: Optional[str] = Field(None, alias="nextAiringEpisode")
    #relations: Relations = Relations(edges=[])
    
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    source: Optional[str] = None
    synonyms: Optional[List[str]] = None
    
    # manga
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    
    #imdb_id: Optional[str] = Field(None, alias="imdbId")
    original_language: str = Field(..., alias="originalLanguage")
    
    # movie
    release_date: Optional[str] = Field(None, alias="releaseDate")
    #belongs_to_collection: Optional[TMDBBelongsToCollection] = Field(
    #    None, alias="belongsToCollection"
    #)
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    
    # tv
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    created_by: Optional[str] = Field(None, alias="createdBy")
    episode_run_time: Optional[int] = Field(None, alias="episodeRunTime")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    last_air_date: Optional[str] = Field(None, alias="lastAirDate")
    #next_episode_to_air: Optional[TMDBLastEpisodeToAir] = Field(None, alias="nextEpisodeToAir")
    number_of_episodes: Optional[int] = Field(None, alias="numberOfEpisodes")
    number_of_seasons: Optional[int] = Field(None, alias="numberOfSeasons")
    #seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaFeaturedBulk(BaseModel):
    trending: Optional[List[MediaMinimal]] = None
    popular_season: Optional[List[MediaMinimal]] = Field(default=None, alias="popularSeason")
    upcoming: Optional[List[MediaMinimal]] = None
    all_time: Optional[List[MediaMinimal]] = Field(default=None, alias="allTime")
    all_time_manhwa: Optional[List[MediaMinimal]] = Field(default=None, alias="allTimeManhwa")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
