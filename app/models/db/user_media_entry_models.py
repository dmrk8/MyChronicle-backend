from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    MediaType,
    UserMediaEntryStatus,
)


class UserMediaEntryCreate(BaseModel):
    external_id: int = Field(
        ...,
        alias="externalId",
        description="The external ID of the media from the source API",
    )
    external_source: MediaExternalSource = Field(
        ...,
        alias="externalSource",
        description="The source of the media (e.g., AniList, TMDB, IGDB)",
    )
    media_type: MediaType = Field(
        ...,
        alias="mediaType",
        description="The type of media (e.g., anime, manga, game, movie, TV)",
    )
    title: str = Field(..., alias="title", description="The title of the media")
    cover_image: Optional[str] = Field(
        None, alias="coverImage", description="The cover image URL of the media"
    )
    is_adult: Optional[bool] = Field(
        False, alias="isAdult", description="Whether the media is adult content"
    )
    status: Optional[UserMediaEntryStatus] = Field(
        UserMediaEntryStatus.PLANNING,
        alias="status",
        description="The user's consumption status for the media",
    )
    repeat_count: Optional[int] = Field(
        0,
        alias="repeatCount",
        description="How many times the user has consumed the media",
    )
    is_favorite: Optional[bool] = Field(
        False,
        alias="isFavorite",
        description="Whether the user has marked this media as a favorite",
    )
    in_library: Optional[bool] = Field(
        True,
        alias="inLibrary",
        description="Whether the media is in the user's personal library",
    )

    @field_validator("repeat_count")
    @classmethod
    def repeat_count_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("repeat_count must be non-negative")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryInsert(UserMediaEntryCreate):
    user_id: str = Field(...)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values):
        now = datetime.now(timezone.utc)
        values.setdefault("created_at", now)
        values.setdefault("updated_at", now)
        return values


class UserMediaEntryDB(UserMediaEntryInsert):
    id: str = Field(..., alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)


class UserMediaEntryUpdate(BaseModel):
    """User preference updates"""

    status: Optional[UserMediaEntryStatus] = Field(None, alias="status")
    repeat_count: Optional[int] = Field(None, alias="repeatCount")
    is_favorite: Optional[bool] = Field(None, alias="isFavorite")
    in_library: Optional[bool] = Field(None, alias="inLibrary")

    def to_update_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True, by_alias=False)
        if not data:
            raise ValueError("No fields provided for update")
        data["updated_at"] = datetime.now(timezone.utc)
        return data

    @field_validator("repeat_count")
    @classmethod
    def repeat_count_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("repeat_count must be non-negative")
        return v

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
    
    def to_update_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True, by_alias=False)
        if not data:
            raise ValueError("No fields provided for update")
        return data

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntry(BaseModel):
    id: str
    external_id: int = Field(..., alias="externalId")
    external_source: MediaExternalSource = Field(..., alias="externalSource")
    media_type: MediaType = Field(..., alias="mediaType")
    user_id: str = Field(..., alias="userId")
    title: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    status: Optional[UserMediaEntryStatus] = None
    repeat_count: Optional[int] = Field(None, alias="repeatCount")
    is_favorite: Optional[bool] = Field(None, alias="isFavorite")
    in_library: Optional[bool] = Field(None, alias="inLibrary")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )

    @classmethod
    def from_db(cls, entry: UserMediaEntryDB) -> "UserMediaEntry":
        return cls(**entry.model_dump())


class UserMediaEntryPagination(BaseModel):
    results: List[UserMediaEntry] = Field(...)
    page: int = Field(..., alias="page", description="Current page number")
    per_page: int = Field(..., alias="perPage", description="Number of items per page")
    has_next_page: bool = Field(
        ..., alias="hasNextPage", description="Is there a next page?"
    )
    total: int = Field(..., description="Total number of items")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
