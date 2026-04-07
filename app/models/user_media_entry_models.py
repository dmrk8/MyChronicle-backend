from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    MediaType,
    UserMediaEntryStatus,
)


class UserMediaEntryBase(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = Field(None, alias="coverImage")
    is_adult: Optional[bool] = Field(None, alias="isAdult")

    status: Optional[UserMediaEntryStatus] = Field(None)
    repeat_count: Optional[int] = Field(None, alias="repeatCount")
    is_favorite: Optional[bool] = Field(None, alias="isFavorite")
    in_library: Optional[bool] = Field(None, alias="inLibrary")

    @field_validator("repeat_count")
    @classmethod
    def repeat_count_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("repeat_count must be non-negative")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryCreate(UserMediaEntryBase):
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


class UserMediaEntryDB(UserMediaEntryBase):
    id: str = Field(..., alias="_id")

    external_id: int = Field(...)
    external_source: MediaExternalSource = Field(...)
    media_type: MediaType = Field(...)

    user_id: str = Field(...)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)


class UserMediaEntryUpdate(BaseModel):
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
