from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class Title(BaseModel):
    english: Optional[str] = None
    romaji: Optional[str] = None
    native: Optional[str] = None


class NextAiringEpisode(BaseModel):
    episode: Optional[int] = None
    airing_at: Optional[int] = Field(None, alias="airingAt")
    time_until_airing: Optional[int] = Field(None, alias="timeUntilAiring")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaDate(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class CoverImage(BaseModel):
    medium: Optional[str] = None
    large: Optional[str] = None
    extra_large: Optional[str] = Field(None, alias="extraLarge")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Tag(BaseModel):
    name: str
    is_media_spoiler: bool = Field(..., alias="isMediaSpoiler")
    is_general_spoiler: bool = Field(..., alias="isGeneralSpoiler")
    rank: int

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RelationNode(BaseModel):
    id: int
    title: Title
    format: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[CoverImage] = Field(None, alias="coverImage")
    type: str
    

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RelationEdge(BaseModel):
    relation_type: str = Field(..., alias="relationType")
    node: RelationNode

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Relations(BaseModel):
    edges: List[RelationEdge]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class StudioNode(BaseModel):
    id: int
    name: str


class StudioEdge(BaseModel):
    is_main: bool = Field(..., alias="isMain")
    node: StudioNode

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Studios(BaseModel):
    edges: List[StudioEdge]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class CharacterImage(BaseModel):
    large: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class CharacterName(BaseModel):
    full: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class VoiceActorName(BaseModel):
    full: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class VoiceActorImage(BaseModel):
    large: Optional[str] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class VoiceActor(BaseModel):
    name: VoiceActorName
    image: VoiceActorImage

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class CharacterNode(BaseModel):
    image: CharacterImage
    name: CharacterName

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class CharacterEdge(BaseModel):
    node: CharacterNode
    role: str
    voice_actors: Optional[List[VoiceActor]] = Field(None, alias="voiceActors")  

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Characters(BaseModel):
    edges: List[CharacterEdge]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RecommendationMedia(BaseModel):
    id: int
    title: Title
    cover_image: Optional[CoverImage] = Field(None, alias="coverImage")
    format: Optional[str] = None
    status: Optional[str] = None
    type: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RecommendationNode(BaseModel):
    media_recommendation: Optional[RecommendationMedia] = Field(None, alias="mediaRecommendation")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class RecommendationEdge(BaseModel):
    node: RecommendationNode

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class Recommendations(BaseModel):
    edges: List[RecommendationEdge]

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AnilistMediaMinimal(BaseModel):
    id: int = Field(..., alias="id")
    type: str
    title: Title
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    episodes: Optional[int] = None
    duration: Optional[int] = None
    chapters: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[MediaDate] = Field(None, alias="startDate")
    end_date: Optional[MediaDate] = Field(None, alias="endDate")
    next_airing_episode: Optional[NextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )
    studios: Studios = Studios(edges=[])
    cover_image: Optional[CoverImage] = Field(None, alias="coverImage")
    banner_image: Optional[str] = Field(None, alias="bannerImage")
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    average_score: Optional[int] = Field(None, alias="averageScore")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AnilistMediaDetailed(BaseModel):
    id: int
    average_score: Optional[int] = Field(None, alias="averageScore")
    banner_image: Optional[str] = Field(None, alias="bannerImage")
    chapters: Optional[int] = None
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    cover_image: CoverImage = Field(..., alias="coverImage")
    description: Optional[str] = None
    duration: Optional[int] = None
    end_date: Optional[MediaDate] = Field(None, alias="endDate")
    episodes: Optional[int] = None
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    next_airing_episode: Optional[NextAiringEpisode] = Field(
        None, alias="nextAiringEpisode"
    )
    relations: Relations = Relations(edges=[])
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    source: Optional[str] = None
    start_date: Optional[MediaDate] = Field(None, alias="startDate")
    status: Optional[str] = None
    synonyms: Optional[List[str]] = None
    title: Title
    type: str
    volumes: Optional[int] = None
    tags: List[Tag] = []
    studios: Studios = Studios(edges=[])
    recommendations: Optional[Recommendations] = None
    characters: Optional[Characters] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AnilistPageInfo(BaseModel):
    current_page: int = Field(..., alias="currentPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
    per_page: int = Field(..., alias="perPage")
    total: int

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AnilistPagination(BaseModel):
    results: List[AnilistMediaMinimal]
    current_page: int = Field(..., alias="currentPage")
    per_page: int = Field(..., alias="perPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
    total: int

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class AnilistFeaturedMediaResponse(BaseModel):
    trending: Optional[List[AnilistMediaMinimal]] = None
    popular_season: Optional[List[AnilistMediaMinimal]] = Field(
        default=None, alias="popularSeason"
    )
    upcoming: Optional[List[AnilistMediaMinimal]] = None
    all_time: Optional[List[AnilistMediaMinimal]] = Field(default=None, alias="allTime")
    all_time_manhwa: Optional[List[AnilistMediaMinimal]] = Field(
        default=None, alias="allTimeManhwa"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
