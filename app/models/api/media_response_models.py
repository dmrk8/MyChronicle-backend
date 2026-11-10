from pydantic import Field
from typing import Annotated, List, Literal, Optional

from app.enums.media_enums import MediaExternalSource, MediaStatus, MediaType

from app.models.shared.base import CamelModel
from app.models.shared.media import MediaTag, MediaTitle, MediaScore


class Trailer(CamelModel):
    url: Optional[str] = None
    thumbnail: Optional[str] = None


class MediaStudio(CamelModel):
    is_main: bool
    name: str


class MediaRelation(CamelModel):
    id: int
    media_type: MediaType
    relation_type: Optional[str] = None
    title: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[str] = None


class MediaRecommendation(CamelModel):
    id: int
    title: Optional[str]
    cover_image: Optional[str] = None
    media_type: MediaType


class MediaVoiceActor(CamelModel):
    image: str
    name: str


class MediaCharacter(CamelModel):
    role: str
    image: str
    name: str
    voice_actor: Optional[MediaVoiceActor] = None


class MediaCastMember(CamelModel):
    name: str
    character: Optional[str] = None
    image: Optional[str] = None


class UpcomingEpisode(CamelModel):
    episode_number: Optional[int] = None
    airing_at: Optional[str] = None
    season_number: Optional[int] = None


class LastEpisodeToAir(CamelModel):
    name: Optional[str] = None
    overview: Optional[str] = None
    air_date: Optional[str] = None
    episode_number: Optional[int] = None
    episode_type: Optional[str] = None
    runtime: Optional[int] = None
    season_number: Optional[int] = None
    still_image: Optional[str] = None


class TVSeason(CamelModel):
    air_date: Optional[str] = None
    episode_count: int
    name: str
    overview: str
    poster_image: Optional[str] = None
    season_number: int


class MediaBelongsToCollection(CamelModel):
    id: int
    name: str
    poster_image: Optional[str] = None
    banner_image: Optional[str] = None


class MovieCollectionPart(CamelModel):
    banner_image: Optional[str] = None
    id: int
    title: str
    original_title: str
    media_type: MediaType
    release_date: str
    poster_image: Optional[str] = None


class MovieCollection(CamelModel):
    id: int
    name: str
    overview: Optional[str] = None
    poster_image: Optional[str] = None
    banner_image: Optional[str] = None
    parts: List[MovieCollectionPart] = Field(default_factory=list)


############### Media Response Models ###############
class MediaBase(CamelModel):
    title: MediaTitle
    description: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)

    format: Optional[str] = Field(
        None, description="Media format, e.g. TV, OVA, Movie, Manga, Scripted etc."
    )
    status: Optional[str] = None
    is_adult: Optional[bool] = None
    content_rating: Optional[str] = Field(
        None, description="Content rating, e.g. PG-13, R, etc."
    )

    genres: List[str] = Field(default_factory=list)
    tags: List[MediaTag] = Field(default_factory=list)

    country_of_origin: Optional[str] = None

    # --- Media Assets ---
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    trailer: List[Trailer] = Field(default_factory=list)

    # --- Scores ---
    scores: List[MediaScore] = Field(default_factory=list)

    recommendations: List[MediaRecommendation] = Field(default_factory=list)


class AniMediaData(MediaBase):
    # --- External IDs ---
    id_mal: Optional[int] = None

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # --- Production ---
    source: Optional[str] = None

    # --- Metadata & Relations ---
    relations: List[MediaRelation] = Field(default_factory=list)
    characters: List[MediaCharacter] = Field(default_factory=list)

    background: Optional[str] = Field(
        None,
        description="Background information about the media, such as production details, trivia, etc.",
    )


class AnimeData(AniMediaData):
    media_type: Literal[MediaType.ANIME] = MediaType.ANIME

    # --- Content Structure ---
    episodes: Optional[int] = None
    duration: Optional[int] = None

    # --- Dates & Season ---
    season: Optional[str] = None
    season_year: Optional[int] = None

    # --- Airing Info ---
    next_airing_episode: Optional[UpcomingEpisode] = None

    # --- Production ---
    studios: Optional[List[MediaStudio]] = None


class MangaData(AniMediaData):
    media_type: Literal[MediaType.MANGA] = MediaType.MANGA

    # --- Content Structure ---
    chapters: Optional[int] = None
    volumes: Optional[int] = None

    authors: List[str] = Field(default_factory=list)


class MovieTVMediaBase(MediaBase):
    original_language: Optional[str] = None

    cast: List[MediaCastMember] = Field(default_factory=list)


class MovieData(MovieTVMediaBase):
    media_type: Literal[MediaType.MOVIE] = MediaType.MOVIE

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


class TVData(MovieTVMediaBase):
    media_type: Literal[MediaType.TV] = MediaType.TV

    # --- Dates ---
    first_air_date: Optional[str] = None
    last_air_date: Optional[str] = None
    # --- Content Structure ---
    number_of_episodes: Optional[int] = None
    number_of_seasons: Optional[int] = None

    # --- Airing Info ---
    next_airing_episode: Optional[UpcomingEpisode] = None
    last_episode_to_air: Optional[LastEpisodeToAir] = None
    # --- Production ---
    created_by: List[str] = Field(default_factory=list)
    networks: List[str] = Field(default_factory=list)
    production_countries: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    in_production: Optional[bool] = None

    # --- Structure ---
    seasons: List[TVSeason] = Field(default_factory=list)
    type: Optional[str] = None  # Scripted, Documentary, etc.


class AnimeDetail(AnimeData):
    id: str


class MangaDetail(MangaData):
    id: str


class MovieDetail(MovieData):
    id: str
    collection: Optional[MovieCollection] = None


class TVDetail(TVData):
    id: str


NormalizedMedia = Annotated[
    AnimeData | MangaData | MovieData | TVData, Field(discriminator="media_type")
]

MediaDetail = Annotated[
    AnimeDetail | MangaDetail | MovieDetail | TVDetail,
    Field(discriminator="media_type"),
]


class MediaMinimal(CamelModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    # shared
    title: Optional[str] = Field(description="Flattned title for display purposes")
    format: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    status: Optional[str] = None
    cover_image: Optional[str] = None
    average_score: Optional[float] = None
    banner_image: Optional[str] = None

    # anime
    episodes: Optional[int] = None
    main_studio: Optional[str] = None

    # manga
    chapters: Optional[int] = None

    # movie
    release_date: Optional[str] = None

    # tv
    first_air_date: Optional[str] = None


class MediaPagination(CamelModel):
    results: List[MediaMinimal]
    current_page: int
    per_page: Optional[int] = None
    has_next_page: bool
    total: Optional[int] = None
