from datetime import datetime, timezone
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


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
        default_factory=lambda: datetime.now(timezone.utc),
        alias="createdAt",
        description="The date when the review was added to the system",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        alias="updatedAt",
        description="The date when the review was last updated",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewUpdate(BaseModel):
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

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewResponse(BaseModel):
    message: str = Field(description="Response message")
    acknowledged: Optional[bool] = Field(
        None, description="Whether the operation was acknowledged by the database"
    )
    data: Optional[ReviewDB | List[ReviewDB]] = None
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
