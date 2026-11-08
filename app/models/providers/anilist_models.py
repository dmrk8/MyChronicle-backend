from pydantic import Field
from typing import List, Optional

from app.models.shared.base import CamelModel


class Title(CamelModel):
    english: Optional[str] = None
    romaji: Optional[str] = None
    native: Optional[str] = None


class NextAiringEpisode(CamelModel):
    episode: Optional[int] = None
    airing_at: Optional[int] = None
    time_until_airing: Optional[int] = None


class MediaDate(CamelModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class CoverImage(CamelModel):
    medium: Optional[str] = None
    large: Optional[str] = None
    extra_large: Optional[str] = None


class Tag(CamelModel):
    name: str
    is_media_spoiler: bool 
    is_general_spoiler: bool
    rank: int
    description: str
    category: str


class RelationNode(CamelModel):
    id: int
    title: Title
    format: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[CoverImage] = None
    type: str


class RelationEdge(CamelModel):
    relation_type: str 
    node: RelationNode


class Relations(CamelModel):
    edges: List[RelationEdge]


class StudioNode(CamelModel):
    id: int
    name: str


class StudioEdge(CamelModel):
    is_main: bool = Field(...)
    node: StudioNode


class Studios(CamelModel):
    edges: List[StudioEdge]


class CharacterImage(CamelModel):
    large: Optional[str] = None


class CharacterName(CamelModel):
    full: str


class VoiceActorName(CamelModel):
    full: str


class VoiceActorImage(CamelModel):
    large: Optional[str] = None


class VoiceActor(CamelModel):
    name: VoiceActorName
    image: VoiceActorImage


class CharacterNode(CamelModel):
    image: CharacterImage
    name: CharacterName


class CharacterEdge(CamelModel):
    node: CharacterNode
    role: str
    voice_actors: Optional[List[VoiceActor]] = None


class Characters(CamelModel):
    edges: List[CharacterEdge]


class RecommendationMedia(CamelModel):
    id: int
    title: Title
    cover_image: Optional[CoverImage] = None
    format: Optional[str] = None
    status: Optional[str] = None
    type: str


class RecommendationNode(CamelModel):
    media_recommendation: Optional[RecommendationMedia] = None


class RecommendationEdge(CamelModel):
    node: RecommendationNode


class Recommendations(CamelModel):
    edges: List[RecommendationEdge]


class AnilistTrailer(CamelModel):
    id: Optional[str] = None  
    site: Optional[str] = None
    thumbnail: Optional[str] = None



class AnilistMediaMinimal(CamelModel):
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
    weighted_score: Optional[int] = None

    # --- Media Assets ---
    cover_image: Optional[CoverImage] = None
    banner_image: Optional[str] = None

    # --- Airing Info ---
    next_airing_episode: Optional[NextAiringEpisode] = None

    # --- Relations ---
    studios: Optional[Studios] = None


class AnilistMediaDetail(CamelModel):
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
    weighted_score: Optional[int] = None
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


class AnilistPageInfo(CamelModel):
    current_page: int
    has_next_page: bool
    per_page: int
    total: int


class AnilistPagination(CamelModel):
    results: List[AnilistMediaMinimal]
    current_page: int
    per_page: int
    has_next_page: bool
    total: int
