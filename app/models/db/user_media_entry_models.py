from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.enums.media_enums import  MediaType
from app.enums.user_media_entry_enums import UserMediaEntryStatus
from app.models.db.base import SoftDeleteDBBase


class UserMediaEntryCreate(BaseModel):
    media_id: UUID = Field(
        ..., alias="mediaId", description="The internal ID of the media in the system"
    )

    media_type: MediaType = Field(
        ...,
        alias="mediaType",
        description="The type of media (e.g., anime, manga, game, movie, TV)",
    )

    # Metadata
    title: str = Field(..., alias="title", description="The title of the media")
    cover_image: Optional[str] = Field(
        None, alias="coverImage", description="The cover image URL of the media"
    )
    is_adult: Optional[bool] = Field(
        False, alias="isAdult", description="Whether the media is adult content"
    )

    # User-specific fields
    status: UserMediaEntryStatus = Field(
        UserMediaEntryStatus.PLANNING,
        alias="status",
        description="The user's consumption status for the media",
    )
    is_favorite: bool = Field(
        False,
        alias="isFavorite",
        description="Whether the user has marked this media as a favorite",
    )
    repeat_count: Optional[int] = Field(
        None,
        ge=0,
        alias="repeatCount",
        description="How many times the user has consumed the media",
    )

    score: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="User's score for the media, independent of reviews",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryInsert(UserMediaEntryCreate):
    user_id: UUID = Field(...)


class UserMediaEntryUpdate(BaseModel):
    status: Optional[UserMediaEntryStatus] = Field(None, alias="status")
    repeat_count: Optional[int] = Field(None, ge=0, alias="repeatCount")
    is_favorite: Optional[bool] = Field(None, alias="isFavorite")
    score: Optional[float] = Field(None, ge=0, le=10, alias="score")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntrySyncMetadata(BaseModel):
    """Metadata sync from external APIs"""

    title: Optional[str] = Field(
        None, alias="title", description="Synced title from external API"
    )
    cover_image: Optional[str] = Field(
        None, alias="coverImage", description="Synced cover image URL"
    )
    is_adult: Optional[bool] = Field(
        None, alias="isAdult", description="Synced adult status"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryDB(SoftDeleteDBBase):
    media_id: UUID
    media_type: MediaType
    user_id: UUID
    title: Optional[str] = None
    cover_image: Optional[str] = None
    is_adult: Optional[bool] = None
    status: Optional[UserMediaEntryStatus] = None
    repeat_count: Optional[int] = None
    is_favorite: Optional[bool] = None
    score: Optional[float] = None


class UserMediaEntry(BaseModel):
    """The main model used for API responses"""

    id: UUID = Field(..., alias="id", description="The unique ID of the user media entry")
    media_id: UUID = Field(..., alias="mediaId")
    media_type: MediaType = Field(..., alias="mediaType")
    user_id: UUID = Field(..., alias="userId")
    title: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    status: Optional[UserMediaEntryStatus] = None
    repeat_count: Optional[int] = Field(None, alias="repeatCount")
    is_favorite: Optional[bool] = Field(None, alias="isFavorite")
    score: Optional[float] = None

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )


class UserMediaEntryPagination(BaseModel):
    results: List[UserMediaEntry] = Field(...)
    page: int = Field(..., alias="page", description="Current page number")
    per_page: int = Field(..., alias="perPage", description="Number of items per page")
    has_next_page: bool = Field(
        ..., alias="hasNextPage", description="Is there a next page?"
    )
    total: int = Field(..., description="Total number of items")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
