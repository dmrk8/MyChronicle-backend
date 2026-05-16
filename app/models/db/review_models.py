from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.db.base import DBBase


class ReviewCreate(BaseModel):
    review: str = Field(
        ...,
        max_length=5000,
    )
    rating: float = Field(
        ...,
        ge=0,
        le=10,
    )
    review_progress: int = Field(
        ...,
        ge=0,
        alias="reviewProgress",
        description="The chapter or episode progress at the time the review was written",
    )
    written_at: datetime = Field(
        ...,
        alias="writtenAt",
        description="The date when the user wrote the review",
    )

    @field_validator("written_at")
    @classmethod
    def validate_written_at(cls, v: datetime | None):
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        candidate = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if candidate > now:
            raise ValueError("Written at date cannot be in the future")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewInsert(ReviewCreate):
    user_media_entry_id: str
    user_id: str


class ReviewUpdate(BaseModel):
    review: Optional[str] = Field(
        None,
        max_length=5000,
    )
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=10,
    )
    review_progress: Optional[int] = Field(
        None,
        ge=0,
        alias="reviewProgress",
        description="The chapter or episode progress at the time the review was written",
    )
    written_at: Optional[datetime] = Field(
        None,
        alias="writtenAt",
        description="The date when the user wrote the review",
    )

    @field_validator("written_at")
    @classmethod
    def validate_written_at(cls, v: datetime | None):
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        candidate = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if candidate > now:
            raise ValueError("Written at date cannot be in the future")
        return v

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class ReviewDB(DBBase):
    user_media_entry_id: UUID = Field(...)
    user_id: UUID = Field(...)

    review: Optional[str] = None
    rating: Optional[float] = None
    review_progress: Optional[int] = None
    written_at: Optional[datetime] = None


class Review(BaseModel):
    """The main model used for API responses and business logic"""

    id: str
    user_media_entry_id: str = Field(..., alias="userMediaEntryId")
    user_id: str = Field(..., alias="userId")

    review: Optional[str] = None
    rating: Optional[float] = None
    review_progress: Optional[int] = Field(None, alias="reviewProgress")
    written_at: Optional[datetime] = Field(None, alias="writtenAt")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

