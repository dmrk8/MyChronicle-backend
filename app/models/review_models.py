from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


# Per-review model (unique fields, linked to UserMediaEntry)
class ReviewCreate(BaseModel):
    user_media_entry_id: str = Field(
        ..., alias="userMediaEntryId", description="The ID of the associated UserMediaEntry"
    )
    review: Optional[str] = Field(None, description="The user's written review text")
    rating: Optional[float] = Field(None, description="The user's rating for the media")
    review_progress: Optional[int] = Field(
        None,
        alias="reviewProgress",
        description="The chapter or episode progress at the time the review was written",
    )
    written_at: Optional[datetime] = Field(
        None,
        alias="writtenAt",
        description="The date when the user wrote the review",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewDB(ReviewCreate):
    id: Optional[str] = Field(None, description="The unique ID of the review in the database")
    created_at: datetime = Field(
        alias="createdAt", description="The date when the review was added to the system"
    )
    updated_at: datetime = Field(
        alias="updatedAt", description="The date when the review was last updated"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewUpdate(BaseModel):
    id: str = Field(description="The ID of the review to update")
    review: Optional[str] = Field(None, description="Updated review text")
    rating: Optional[float] = Field(None, description="Updated rating")
    review_progress: Optional[int] = Field(
        None, alias="reviewProgress", description="Updated progress"
    )
    written_at: Optional[datetime] = Field(
        None,
        alias="writtenAt",
        description="The date when the user wrote the review",
    )
    updated_at: Optional[datetime] = Field(
        None, alias="updatedAt", description="Timestamp of the update"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewResponse(BaseModel):
    message: str = Field(description="Response message")
    review_id: Optional[str] = Field(
        None, alias="reviewId", description="ID of the created or updated review"
    )
    user_media_entry_id: Optional[str] = Field(
        None, alias="userMediaEntryId", description="ID of the associated user-media entry"
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
    data: Optional[Any] = Field(
        None, description="Additional data, such as review lists or details"
    )
    acknowledged: Optional[bool] = Field(
        None, description="Whether the operation was acknowledged by the database"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
