
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ReviewCreate(BaseModel):
    media_id: int = Field(..., alias="mediaId")
    type : str
    review: Optional[str]
    rating: Optional[float]
    is_favorite: bool = Field(..., alias="isFavorite")
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class ReviewDB(ReviewCreate):
    id : Optional[str] = None
    user_id : str = Field(..., alias="userId")
    created_at : datetime = Field(alias="createdAt")
    updated_at : datetime = Field(alias="updatedAt")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
class ReviewUpdate(BaseModel):
    id : str
    review: Optional[str] = None
    rating: Optional[float] = None
    is_favorite: Optional[bool] = Field(None, alias="isFavorite")
    updated_at : Optional[datetime] = Field(None, alias="updatedAt")
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class ReviewResponse(BaseModel):
    message: str
    review_id: Optional[str] = Field(None, alias="reviewId")
    matched_count: Optional[int] = Field(None, alias="matchedCount")
    modified_count: Optional[int] = Field(None, alias="modifiedCount")
    deleted_count: Optional[int] = Field(None, alias="deletedCount")
    updated_at: Optional[Any] = Field(None, alias="updatedAt")
    data: Optional[Any] = None  # For returning review data or lists
    acknowledged: Optional[bool] = None
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)