from datetime import datetime, timezone
from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ReviewBase(BaseModel):
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


class ReviewCreate(ReviewBase):
    user_media_entry_id: str = Field(
        ...,
        alias="userMediaEntryId",
    )


class ReviewInsert(ReviewCreate):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )
    user_id: str = Field(..., alias="userId")


class ReviewDB(ReviewBase):
    id: str
    user_media_entry_id: str = Field(
        ...,
        alias="userMediaEntryId",
    )
    user_id: str = Field(..., alias="userId")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt"
    )


class ReviewUpdate(ReviewBase):
    pass
