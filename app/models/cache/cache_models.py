from pydantic import BaseModel
from app.models.api.media_response_models import (
    MediaPagination,
)


class CachedMediaPagination(BaseModel):
    data: MediaPagination
