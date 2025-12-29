from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.enums.review_enums import ReviewMediaType, ReviewMediaSource, ReviewStatus


class UserMediaEntryCreate(BaseModel):
    external_id: int = Field(
        ..., alias="externalId", description="The external ID of the media from the source API"
    )
    source: ReviewMediaSource = Field(
        ...,
        alias="externalSource",
        description="The source of the media (e.g., AniList, TMDB, IGDB)",
    )
    media_type: ReviewMediaType = Field(
        ...,
        alias="mediaType",
        description="The type of media (e.g., anime, manga, game, movie, TV)",
    )
    status: ReviewStatus = Field(
        ReviewStatus.COMPLETED,
        alias="status",
        description="The user's consumption status for the media",
    )
    repeat_count: Optional[int] = Field(
        0, alias="repeatCount", description="How many times the user has consumed the media"
    )
    is_favorite: bool = Field(
        False,
        alias="isFavorite",
        description="Whether the user has marked this media as a favorite",
    )
    in_library: bool = Field(
        False, alias="inLibrary", description="Whether the media is in the user's personal library"
    )

    @field_validator("repeat_count")
    @classmethod
    def repeat_count_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("repeat_count must be non-negative")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryDB(UserMediaEntryCreate):
    id: Optional[str] = Field(
        None, description="The unique ID of the user-media entry in the database"
    )
    user_id: str = Field(..., alias="userId", description="The ID of the user")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryUpdate(BaseModel):
    status: Optional[ReviewStatus] = Field(
        None, alias="status", description="Updated consumption status"
    )
    repeat_count: Optional[int] = Field(
        None, alias="repeatCount", description="Updated repeat count"
    )
    is_favorite: Optional[bool] = Field(
        None, alias="isFavorite", description="Updated favorite status"
    )
    in_library: Optional[bool] = Field(
        None, alias="inLibrary", description="Updated library status"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )

    @field_validator("repeat_count")
    @classmethod
    def repeat_count_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("repeat_count must be non-negative")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryResponse(BaseModel):
    message: str = Field(description="Response message")
    data: Optional[UserMediaEntryDB | List[UserMediaEntryDB]] = Field(
        None, description="Additional data, such as media details"
    )
    acknowledged: Optional[bool] = Field(
        None, description="Whether the operation was acknowledged by the database"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryPagination(BaseModel):
    results: List[UserMediaEntryDB] = Field(..., alias="results")
    page: int = Field(..., alias="page", description="Current page number")
    per_page: int = Field(..., alias="perPage", description="Number of items per page")
    has_next_page: bool = Field(..., alias="hasNextPage", description="Is there a next page?")
    total: int = Field(..., alias="total", description="Total number of items")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
