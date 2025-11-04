
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ReviewCreate(BaseModel):
    media_id: int
    title: str
    type : str
    review: str
    rating: float

class ReviewDB(ReviewCreate):
    id : Optional[str] = None
    user_id : str
    created_at : datetime
    updated_at : datetime

class ReviewUpdate(BaseModel):
    id : str
    review: Optional[str] = None
    rating: Optional[float] = None


