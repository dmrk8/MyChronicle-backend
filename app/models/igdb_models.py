from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class IGDBAlternativeName(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBArtwork(BaseModel):
    id: int
    url: Optional[str] = Field(default=None, alias="url")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBCover(BaseModel):
    id: int
    url: Optional[str] = Field(default=None, alias="url")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameType(BaseModel):
    id: int
    type: Optional[str] = Field(default=None, alias="type")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGame(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")
    game_type: Optional[IGDBGameType] = Field(default=None, alias="gameType")
    version_parent: Optional[int] = Field(default=None, alias="versionParent")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBFranchise(BaseModel):
    id: int
    games: Optional[List[IGDBGame]] = Field(default=None, alias="games")
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameMode(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGenre(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBCompany(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBInvolvedCompany(BaseModel):
    id: int
    company: Optional[IGDBCompany] = Field(default=None, alias="company")
    developer: Optional[bool] = Field(default=None, alias="developer")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBKeyword(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBPlatform(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBPlayerPerspective(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBTheme(BaseModel):
    id: int
    name: Optional[str] = Field(default=None, alias="name")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameDetail(BaseModel):
    id: int
    aggregated_rating: Optional[float] = Field(default=None, alias="aggregatedRating")
    aggregated_rating_count: Optional[int] = Field(default=None, alias="aggregatedRatingCount")
    alternative_names: Optional[List[IGDBAlternativeName]] = Field(
        default=None, alias="alternativeNames"
    )
    artworks: Optional[List[IGDBArtwork]] = Field(default=None, alias="artworks")
    cover: Optional[IGDBCover] = Field(default=None, alias="cover")
    first_release_date: Optional[int] = Field(default=None, alias="firstReleaseDate")
    franchises: Optional[List[IGDBFranchise]] = Field(default=None, alias="franchises")
    game_modes: Optional[List[IGDBGameMode]] = Field(default=None, alias="gameModes")
    genres: Optional[List[IGDBGenre]] = Field(default=None, alias="genres")
    involved_companies: Optional[List[IGDBInvolvedCompany]] = Field(
        default=None, alias="involvedCompanies"
    )
    keywords: Optional[List[IGDBKeyword]] = Field(default=None, alias="keywords")
    name: Optional[str] = Field(default=None, alias="name")
    platforms: Optional[List[IGDBPlatform]] = Field(default=None, alias="platforms")
    player_perspectives: Optional[List[IGDBPlayerPerspective]] = Field(
        default=None, alias="playerPerspectives"
    )
    storyline: Optional[str] = Field(default=None, alias="storyline")
    summary: Optional[str] = Field(default=None, alias="summary")
    themes: Optional[List[IGDBTheme]] = Field(default=None, alias="themes")
    total_rating: Optional[float] = Field(default=None, alias="totalRating")
    total_rating_count: Optional[int] = Field(default=None, alias="totalRatingCount")
    game_type: Optional[IGDBGameType] = Field(default=None, alias="gameType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameMinimal(BaseModel):
    id: int
    aggregated_rating: Optional[float] = Field(default=None, alias="aggregatedRating")
    cover: Optional[IGDBCover] = Field(default=None, alias="cover")
    first_release_date: Optional[int] = Field(default=None, alias="firstReleaseDate")
    genres: Optional[List[IGDBGenre]] = Field(default=None, alias="genres")
    involved_companies: Optional[List[IGDBInvolvedCompany]] = Field(
        default=None, alias="involvedCompanies"
    )
    name: Optional[str] = Field(default=None, alias="name")
    game_type: Optional[IGDBGameType] = Field(default=None, alias="gameType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBGameMinimalResponse(BaseModel):
    id: int
    aggregated_rating: Optional[float] = Field(default=None, alias="aggregatedRating")
    cover: Optional[IGDBCover] = Field(default=None, alias="cover")
    first_release_date: Optional[int] = Field(default=None, alias="firstReleaseDate")
    genres: Optional[List[IGDBGenre]] = Field(default=None, alias="genres")
    developer_company: Optional[str] = Field(default=None, alias="developerCompany")
    name: Optional[str] = Field(default=None, alias="name")
    game_type: Optional[IGDBGameType] = Field(default=None, alias="gameType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBPageInfo(BaseModel):
    offset: Optional[int] = Field(default=None, alias="offset")
    limit: Optional[int] = Field(default=None, alias="limit")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBPagination(BaseModel):
    results: Optional[List[IGDBGameMinimalResponse]] = Field(default=None, alias="results")
    current_page: Optional[int] = Field(default=None, alias="currentPage")
    per_page: Optional[int] = Field(default=None, alias="perPage")
    has_next_page: Optional[bool] = Field(default=None, alias="hasNextPage")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class IGDBToken(BaseModel):
    access_token: str = Field(alias="accessToken")
    expires_in: int = Field(alias="expiresIn")
    token_type: str = Field(alias="tokenType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
