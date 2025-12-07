from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class IGDBAlternativeName(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBArtwork(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBCover(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameType(BaseModel):
    id: int
    type: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGame(BaseModel):
    id: int
    name: str
    game_type: Optional[IGDBGameType] = Field(alias="gameType")
    version_parent: Optional[int] = Field(alias="versionParent")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBFranchise(BaseModel):
    id: int
    games: List[IGDBGame]
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameMode(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGenre(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBCompany(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBInvolvedCompany(BaseModel):
    id: int
    company: IGDBCompany
    developer: bool

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBKeyword(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBPlatform(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBPlayerPerspective(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBTheme(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameDetail(BaseModel):
    id: int
    aggregated_rating: Optional[float] = Field(alias="aggregatedRating")
    aggregated_rating_count: Optional[int] = Field(alias="aggregatedRatingCount")
    alternative_names: List[IGDBAlternativeName] = Field(alias="alternativeNames")
    artworks: List[IGDBArtwork]
    cover: Optional[IGDBCover] = None
    first_release_date: Optional[int] = Field(alias="firstReleaseDate")
    franchises: List[IGDBFranchise]
    game_modes: List[IGDBGameMode] = Field(alias="gameModes")
    genres: List[IGDBGenre]
    involved_companies: List[IGDBInvolvedCompany] = Field(alias="involvedCompanies")
    keywords: List[IGDBKeyword]
    name: str
    platforms: List[IGDBPlatform]
    player_perspectives: List[IGDBPlayerPerspective] = Field(alias="playerPerspectives")
    storyline: Optional[str] = None
    summary: Optional[str] = None
    themes: List[IGDBTheme]
    total_rating: Optional[float] = Field(alias="totalRating")
    total_rating_count: Optional[int] = Field(alias="totalRatingCount")
    game_type: Optional[IGDBGameType] = Field(alias="gameType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameMinimal(BaseModel):
    id: int
    aggregated_rating: Optional[float] = Field(alias="aggregatedRating")
    cover: Optional[IGDBCover] = None
    first_release_date: Optional[int] = Field(alias="firstReleaseDate")
    genres: List[IGDBGenre]
    involved_companies: List[IGDBInvolvedCompany] = Field(alias="involvedCompanies")
    name: str
    game_type: Optional[IGDBGameType] = Field(alias="gameType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
