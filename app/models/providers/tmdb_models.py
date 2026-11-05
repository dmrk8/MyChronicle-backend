
from pydantic import BaseModel
from typing import List, Optional


class TMDBGenre(BaseModel):
    name: str


class TMDBProductionCompany(BaseModel):
    name: str


class TMDBSpokenLanguage(BaseModel):
    english_name: str


class TMDBBelongsToCollection(BaseModel):
    id: int
    name: str
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None


class TMDBCreatedBy(BaseModel):
    name: str
    original_name: str


class TMDBLastEpisodeToAir(BaseModel):
    name: Optional[str] = None
    overview: Optional[str] = None
    vote_average: Optional[float] = None
    air_date: Optional[str] = None
    episode_number: Optional[int] = None
    episode_type: Optional[str] = None
    runtime: Optional[int] = None
    season_number: Optional[int] = None
    still_path: Optional[str] = None


class TMDBNextEpisodeToAir(BaseModel):
    air_date: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None


class TMDBNetwork(BaseModel):
    name: str


class TMDBSeason(BaseModel):
    air_date: Optional[str] = None
    episode_count: int
    name: str
    overview: str
    poster_path: Optional[str] = None
    season_number: int


class TMDBKeyword(BaseModel):
    name: str


class TMDBTvKeywords(BaseModel):
    results: List[TMDBKeyword]


class TMDBMovieKeywords(BaseModel):
    keywords: List[TMDBKeyword]


class TMDBExternalIds(BaseModel):
    imdb_id: Optional[str] = None
    freebase_mid: Optional[str] = None
    freebase_id: Optional[str] = None
    tvdb_id: Optional[int] = None
    tvrage_id: Optional[int] = None
    wikidata_id: Optional[str] = None
    facebook_id: Optional[str] = None
    instagram_id: Optional[str] = None
    twitter_id: Optional[str] = None


class TMDBCollectionPart(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = None
    id: int
    title: str
    original_title: str
    media_type: str
    release_date: str
    poster_path: Optional[str] = None


class TMDBCollection(BaseModel):
    id: int
    name: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    parts: Optional[List[TMDBCollectionPart]] = None


class TMDBMediaMinimal(BaseModel):
    adult: bool
    poster_path: Optional[str] = None
    genre_ids: List[int]
    id: int
    original_language: Optional[str] = None
    popularity: Optional[float] = None
    media_type: Optional[str] = None
    vote_average: Optional[float] = None

    # Movie-specific fields
    title: Optional[str] = None
    original_title: Optional[str] = None
    release_date: Optional[str] = None

    # TV-specific fields
    name: Optional[str] = None
    original_name: Optional[str] = None
    first_air_date: Optional[str] = None
    origin_country: Optional[List[str]] = None


class TMDBPageInfo(BaseModel):
    page: int
    total_pages: int
    total_results: int


class TMDBPagination(BaseModel):
    results: List[TMDBMediaMinimal]
    page: int
    total_pages: int
    total_results: int


class TMDBMediaMinimalRecommendation(BaseModel):
    poster_path: Optional[str] = None
    id: int
    media_type: str
    genre_ids: List[int]
    original_language: str

    title: Optional[str] = None
    original_title: Optional[str] = None

    # TV-specific fields
    name: Optional[str] = None
    original_name: Optional[str] = None


class TMDBPaginationRecommendation(BaseModel):
    results: List[TMDBMediaMinimalRecommendation]
    page: int
    total_pages: int
    total_results: int


class TMDBAlternativeTitle(BaseModel):
    title: str


class TMDBAlternativeTitles(BaseModel):
    titles: List[TMDBAlternativeTitle]


class TMDBAlternativeTitlesTv(BaseModel):
    results: List[TMDBAlternativeTitle]


class TMDBCast(BaseModel):
    name: str
    character: Optional[str] = None
    order: Optional[int] = None
    known_for_department: Optional[str] = None
    original_name: Optional[str] = None
    profile_path: Optional[str] = None


class TMDBCredits(BaseModel):
    cast: List[TMDBCast]


class TMDBVideo(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    site: Optional[str] = None
    type: Optional[str] = None
    official: Optional[bool] = None


class TMDBVideos(BaseModel):
    id: Optional[int] = None
    results: List[TMDBVideo]


class TMDBProductionCountry(BaseModel):
    name: str


class TMDBMediaDetailBase(BaseModel):
    # --- Identifiers ---
    id: int
    media_type: Optional[str] = None

    # --- Content Flags ---
    adult: bool
    status: Optional[str] = None

    # --- Titles & Description ---
    overview: Optional[str] = None
    tagline: Optional[str] = None

    # --- Media Details ---
    genres: Optional[List[TMDBGenre]] = None
    original_language: Optional[str] = None
    origin_country: Optional[List[str]] = None

    # --- Media Assets ---
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None

    # --- Production ---
    production_companies: Optional[List[TMDBProductionCompany]] = None
    spoken_languages: Optional[List[TMDBSpokenLanguage]] = None

    # --- Metrics ---
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    
    videos : Optional[TMDBVideos] = None


class TMDBMovieDetail(TMDBMediaDetailBase):
    # --- External IDs ---
    imdb_id: Optional[str] = None

    # --- Titles ---
    title: Optional[str] = None
    original_title: Optional[str] = None

    # --- Dates ---
    release_date: Optional[str] = None

    # --- Content ---
    runtime: Optional[int] = None

    # --- Financials ---
    budget: Optional[int] = None
    revenue: Optional[int] = None

    # --- Collections ---
    belongs_to_collection: Optional[TMDBBelongsToCollection] = None

    # --- Metadata ---
    keywords: Optional[TMDBMovieKeywords] = None
    alternative_titles: Optional[TMDBAlternativeTitles] = None

    # --- Credits & Recommendations ---
    credits: Optional[TMDBCredits] = None
    recommendations: Optional[TMDBPaginationRecommendation] = None

class TMDBTVDetail(TMDBMediaDetailBase):
    # --- Titles ---
    name: Optional[str] = None
    original_name: Optional[str] = None

    # --- Dates ---
    first_air_date: Optional[str] = None
    last_air_date: Optional[str] = None

    # --- Content Structure ---
    number_of_episodes: Optional[int] = None
    number_of_seasons: Optional[int] = None
    seasons: Optional[List[TMDBSeason]] = None
    type: Optional[str] = None

    # --- Airing Info ---
    next_episode_to_air: Optional[TMDBNextEpisodeToAir] = None
    last_episode_to_air: Optional[TMDBLastEpisodeToAir] = None
    in_production: Optional[bool] = None

    # --- Production ---
    created_by: Optional[List[TMDBCreatedBy]] = None
    networks: Optional[List[TMDBNetwork]] = None
    production_countries: Optional[List[TMDBProductionCountry]] = None
    languages: Optional[List[str]] = None

    # --- External IDs ---
    external_ids: Optional[TMDBExternalIds] = None

    # --- Metadata ---
    keywords: Optional[TMDBTvKeywords] = None
    alternative_titles: Optional[TMDBAlternativeTitlesTv] = None

    # --- Credits & Recommendations ---
    credits: Optional[TMDBCredits] = None
    recommendations: Optional[TMDBPaginationRecommendation] = None

