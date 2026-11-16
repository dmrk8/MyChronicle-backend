from typing import Optional
from pydantic import BaseModel


class MALPicture(BaseModel):
    medium: Optional[str] = None
    large: Optional[str] = None


class MALSharedData(BaseModel):
    id: int
    title: str
    main_picture: Optional[MALPicture] = None
    mean: Optional[float] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    num_list_users: Optional[int] = None
    num_scoring_users: Optional[int] = None
    background: Optional[str] = None
class MALAnimeData(MALSharedData):
    rating: Optional[str] = None


class MALMangaData(MALSharedData):
    pass
