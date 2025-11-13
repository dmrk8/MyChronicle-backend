
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    media_id: int = Field(..., serialization_alias="mediaId")
    title: str
    type : str
    review: Optional[str]
    rating: Optional[float]
    is_favorite: bool = Field(..., serialization_alias="isFavorite")

class ReviewDB(ReviewCreate):
    id : Optional[str] = None
    user_id : str = Field(..., serialization_alias="userId")
    created_at : datetime = Field(serialization_alias="createdAt")
    updated_at : datetime = Field(serialization_alias="updatedAt")

class ReviewUpdate(BaseModel):
    id : str
    review: Optional[str] = None
    rating: Optional[float] = None

class ReviewResponse(BaseModel):
    message: str
    review_id: Optional[str] = None
    matched_count: Optional[int] = None
    modified_count: Optional[int] = None
    deleted_count: Optional[int] = None
    updated_at: Optional[Any] = None
    data: Optional[Any] = None  # For returning review data or lists
    acknowledged: Optional[bool] = None