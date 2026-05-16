from typing import List, Optional
from pydantic import BaseModel, Field


# =========================
# Shared Models
# =========================

class ImageSet(BaseModel):
    image_url: Optional[str] = None
    small_image_url: Optional[str] = None
    large_image_url: Optional[str] = None


class Images(BaseModel):
    jpg: Optional[ImageSet] = None
    webp: Optional[ImageSet] = None


class Title(BaseModel):
    type: str
    title: str


class DatePart(BaseModel):
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None


class DateProp(BaseModel):
    from_: Optional[DatePart] = Field(None, alias="from")
    to: Optional[DatePart] = None
    string: Optional[str] = None


class PublishedDate(BaseModel):
    from_: Optional[str] = Field(None, alias="from")
    to: Optional[str] = None
    prop: Optional[DateProp] = None

    

class MALItem(BaseModel):
    mal_id: int
    type: str
    name: str
    url: Optional[str] = None


class RelationEntry(BaseModel):
    mal_id: int
    type: str
    name: str
    url: Optional[str] = None


class Relation(BaseModel):
    relation: str
    entry: List[RelationEntry]


class ExternalLink(BaseModel):
    name: str
    url: Optional[str] = None


# =========================
# Manga Models
# =========================

class MangaData(BaseModel):
    mal_id: int
    url: Optional[str] = None
    images: Optional[Images] = None
    approved: bool

    titles: List[Title]

    title: str
    title_english: Optional[str] = None
    title_japanese: Optional[str] = None
    title_synonyms: List[str] = []

    type: str
    chapters: Optional[int] = None
    volumes: Optional[int] = None

    status: str
    publishing: bool

    published: Optional[PublishedDate] = None

    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    members: Optional[int] = None
    favorites: Optional[int] = None

    synopsis: Optional[str] = None
    background: Optional[str] = None

    authors: List[MALItem] = []
    serializations: List[MALItem] = []

    genres: List[MALItem] = []
    explicit_genres: List[MALItem] = []
    themes: List[MALItem] = []
    demographics: List[MALItem] = []

    relations: List[Relation] = []

    external: List[ExternalLink] = []


class MALMangaResponse(BaseModel):
    data: MangaData


# =========================
# Anime Models
# =========================

class Trailer(BaseModel):
    youtube_id: Optional[str] = None
    url: Optional[str] = None
    embed_url: Optional[str] = None


class Broadcast(BaseModel):
    day: Optional[str] = None
    time: Optional[str] = None
    timezone: Optional[str] = None
    string: Optional[str] = None


class Theme(BaseModel):
    openings: List[str] = []
    endings: List[str] = []


class AnimeData(BaseModel):
    mal_id: int
    url: Optional[str] = None

    images: Optional[Images] = None
    trailer: Optional[Trailer] = None

    approved: bool

    titles: List[Title]

    title: str
    title_english: Optional[str] = None
    title_japanese: Optional[str] = None
    title_synonyms: List[str] = []

    type: str
    source: Optional[str] = None
    episodes: Optional[int] = None

    status: str
    airing: bool

    aired: Optional[PublishedDate] = None

    duration: Optional[str] = None
    rating: Optional[str] = None

    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    members: Optional[int] = None
    favorites: Optional[int] = None

    synopsis: Optional[str] = None
    background: Optional[str] = None

    season: Optional[str] = None
    year: Optional[int] = None

    broadcast: Optional[Broadcast] = None

    producers: List[MALItem] = []
    licensors: List[MALItem] = []
    studios: List[MALItem] = []

    genres: List[MALItem] = []
    explicit_genres: List[MALItem] = []
    themes: List[MALItem] = []
    demographics: List[MALItem] = []

    relations: List[Relation] = []

    theme: Optional[Theme] = None

    external: List[ExternalLink] = []
    streaming: List[ExternalLink] = []


class MALAnimeResponse(BaseModel):
    data: AnimeData