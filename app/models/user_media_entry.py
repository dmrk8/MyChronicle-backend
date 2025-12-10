from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.enums.review_enums import ReviewMediaType, ReviewMediaSource, ReviewStatus


# Per-media model (shared fields, one per user-media)
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
        None, alias="repeatCount", description="How many times the user has consumed the media"
    )
    is_favorite: bool = Field(
        False,
        alias="isFavorite",
        description="Whether the user has marked this media as a favorite",
    )
    in_library: bool = Field(
        False, alias="inLibrary", description="Whether the media is in the user's personal library"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryDB(UserMediaEntryCreate):
    id: Optional[str] = Field(
        None, description="The unique ID of the user-media entry in the database"
    )
    user_id: str = Field(..., alias="userId", description="The ID of the user")
    created_at: datetime = Field(
        alias="createdAt", description="The date when the media entry was added to the system"
    )
    updated_at: datetime = Field(
        alias="updatedAt", description="The date when the media entry was last updated"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryUpdate(BaseModel):
    id: str = Field(description="The ID of the user-media entry to update")
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
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Timestamp of the update"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class UserMediaEntryResponse(BaseModel):
    message: str = Field(description="Response message")
    user_media_entry_id: Optional[str] = Field(
        None, alias="userMediaEntryId", description="ID of the created or updated user-media entry"
    )
    matched_count: Optional[int] = Field(
        None, alias="matchedCount", description="Number of documents matched in the operation"
    )
    modified_count: Optional[int] = Field(
        None, alias="modifiedCount", description="Number of documents modified"
    )
    deleted_count: Optional[int] = Field(
        None, alias="deletedCount", description="Number of documents deleted"
    )
    updated_at: Optional[Any] = Field(
        None, alias="updatedAt", description="Timestamp of the last update"
    )
    data: Optional[Any] = Field(None, description="Additional data, such as media details")
    acknowledged: Optional[bool] = Field(
        None, description="Whether the operation was acknowledged by the database"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
