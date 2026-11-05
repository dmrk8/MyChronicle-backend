from pydantic import Field
from typing import List, Optional

from app.models.shared.base import AniListBaseModel


class Title(AniListBaseModel):
    english: Optional[str] = None
    romaji: Optional[str] = None
    native: Optional[str] = None


class NextAiringEpisode(AniListBaseModel):
    episode: Optional[int] = None
    airing_at: Optional[int] = None
    time_until_airing: Optional[int] = None


class MediaDate(AniListBaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class CoverImage(AniListBaseModel):
    medium: Optional[str] = None
    large: Optional[str] = None
    extra_large: Optional[str] = None


class Tag(AniListBaseModel):
    name: str
    is_media_spoiler: bool 
    is_general_spoiler: bool
    rank: int
    description: str
    category: str


class RelationNode(AniListBaseModel):
    id: int
    title: Title
    format: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[CoverImage] = None
    type: str


class RelationEdge(AniListBaseModel):
    relation_type: str 
    node: RelationNode


class Relations(AniListBaseModel):
    edges: List[RelationEdge]


class StudioNode(AniListBaseModel):
    id: int
    name: str


class StudioEdge(AniListBaseModel):
    is_main: bool = Field(...)
    node: StudioNode


class Studios(AniListBaseModel):
    edges: List[StudioEdge]


class CharacterImage(AniListBaseModel):
    large: Optional[str] = None


class CharacterName(AniListBaseModel):
    full: str


class VoiceActorName(AniListBaseModel):
    full: str


class VoiceActorImage(AniListBaseModel):
    large: Optional[str] = None


class VoiceActor(AniListBaseModel):
    name: VoiceActorName
    image: VoiceActorImage


class CharacterNode(AniListBaseModel):
    image: CharacterImage
    name: CharacterName


class CharacterEdge(AniListBaseModel):
    node: CharacterNode
    role: str
    voice_actors: Optional[List[VoiceActor]] = None


class Characters(AniListBaseModel):
    edges: List[CharacterEdge]


class RecommendationMedia(AniListBaseModel):
    id: int
    title: Title
    cover_image: Optional[CoverImage] = None
    format: Optional[str] = None
    status: Optional[str] = None
    type: str


class RecommendationNode(AniListBaseModel):
    media_recommendation: Optional[RecommendationMedia] = None


class RecommendationEdge(AniListBaseModel):
    node: RecommendationNode


class Recommendations(AniListBaseModel):
    edges: List[RecommendationEdge]


class AnilistTrailer(AniListBaseModel):
    id: Optional[str] = None  
    site: Optional[str] = None
    thumbnail: Optional[str] = None


class AnilistMediaMinimal(AniListBaseModel):
    # --- Identifiers ---
    id: int 
    type: str

    # --- Titles ---
    title: Optional[Title] = None

    # --- Media Details ---
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None

    # --- Dates & Season ---
    season: Optional[str] = None
    season_year: Optional[int] = None
    start_date: Optional[MediaDate] = None
    end_date: Optional[MediaDate] = None

    # --- Content Structure ---
    episodes: Optional[int] = None
    duration: Optional[int] = None
    chapters: Optional[int] = None

    # --- Scores ---
    average_score: Optional[int] = None

    # --- Media Assets ---
    cover_image: Optional[CoverImage] = None
    banner_image: Optional[str] = None

    # --- Airing Info ---
    next_airing_episode: Optional[NextAiringEpisode] = None

    # --- Relations ---
    studios: Optional[Studios] = None


class AnilistMediaDetail(AniListBaseModel):
    # --- Identifiers ---
    id: int
    id_mal: Optional[int] = None
    type: str

    # --- Titles & Description ---
    title: Optional[Title] = None
    description: Optional[str] = None
    synonyms: Optional[List[str]] = None

    # --- Media Details ---
    format: Optional[str] = None
    source: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[Tag]] = None
    is_adult: Optional[bool] = None

    # --- Dates & Season ---
    season: Optional[str] = None
    season_year: Optional[int] = None
    start_date: Optional[MediaDate] = None
    end_date: Optional[MediaDate] = None
    status: Optional[str] = None
    country_of_origin: Optional[str] = None

    # --- Content Structure ---
    episodes: Optional[int] = None
    duration: Optional[int] = None
    chapters: Optional[int] = None
    volumes: Optional[int] = None

    # --- Scores & Popularity ---
    average_score: Optional[int] = None
    popularity: Optional[int] = None

    # --- Media Assets ---
    cover_image: Optional[CoverImage] = None
    banner_image: Optional[str] = None
    trailer: Optional[AnilistTrailer] = None

    # --- Airing Info ---
    next_airing_episode: Optional[NextAiringEpisode] = None

    # --- Relations & Extras ---
    relations: Optional[Relations] = None
    studios: Optional[Studios] = None
    characters: Optional[Characters] = None
    recommendations: Optional[Recommendations] = None


class AnilistPageInfo(AniListBaseModel):
    current_page: int
    has_next_page: bool
    per_page: int
    total: int


class AnilistPagination(AniListBaseModel):
    results: List[AnilistMediaMinimal]
    current_page: int
    per_page: int
    has_next_page: bool
    total: int
