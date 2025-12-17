from typing import Any, List, Optional, Tuple, Dict
from httpx import AsyncClient

from app.models.anilist_models import AnilistMediaDetailed, AnilistMediaMinimal, AnilistPageInfo
from app.enums.anilist_enums import SortOption
from app.integrations.http_helpers import perform_request

ANILIST_URL = "https://graphql.anilist.co"


class AnilistApi:
    def __init__(self, client: AsyncClient):
        self.client = client

    @staticmethod
    def extract_main_studio(studios_data: dict) -> Optional[str]:
        """Extract main studio name from studios edges"""
        if studios_data and studios_data.get("edges"):
            for edge in studios_data["edges"]:
                if edge.get("isMain"):
                    return edge["node"]["name"]
        return None

    async def get_featured_media(
        self,
        page: int,
        per_page: int,
        season: Optional[str],
        season_year: Optional[int],
        sort: str,
        media_type: str,
    ) -> List[AnilistMediaMinimal]:
        """
        Fetches featured media data: all time popular, trending now, popular this season, and upcoming next season.
        Uses the provided GraphQL query with different parameters for each category.
        """

        variables = {"page": page, "perPage": per_page, "sort": [sort], "type": media_type}

        if season:
            variables["season"] = season
        if season_year:
            variables["seasonYear"] = season_year

        graphql_query = {
            "query": """ 
            query($page: Int, $perPage: Int, $type: MediaType, $sort: [MediaSort], $season: MediaSeason, $seasonYear: Int) {
              Page(page: $page, perPage: $perPage) {
                media(type: $type, sort: $sort, season: $season, seasonYear: $seasonYear) {
                  id
                  title {
                    english
                    romaji
                  }
                  format
                  genres
                  episodes
                  duration
                  status
                  nextAiringEpisode {
                    episode
                    airingAt
                    timeUntilAiring
                  }
                  studios {
                    edges {
                      isMain
                      node {
                        id
                        name
                      }
                    }
                  }
                  coverImage {
                    large
                  }
                  season
                  seasonYear
                  averageScore
                }
              }
            }
            """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="get_featured_media",
        )

        media_list = data.get("data", {}).get("Page", {}).get("media", [])

        # Map each media item to AnilistMedia model using model_validate
        featured_media = []
        for media in media_list:
            # Extract main studio
            media["main_studio"] = self.extract_main_studio(media.get("studios"))
            # Get the large cover image
            media["coverImageLarge"] = media.get("coverImage", {}).get("large")

            featured_media.append(AnilistMediaMinimal.model_validate(media))

        
        return featured_media

    async def search_media(
        self,
        page: int,
        per_page: int,
        search: Optional[str],
        media_type: str,
        sort: str,
        season: Optional[str],
        season_year: Optional[int],
        format: Optional[str],
        status: Optional[str],
        genre_in: Optional[List[str]],
        tag_in: Optional[List[str]],
        is_adult: Optional[bool] = None,
        country_of_origin: Optional[str] = None,
    ) -> tuple[List[AnilistMediaMinimal], AnilistPageInfo]:
        """
        Searches for media based on the provided parameters.
        Uses the provided GraphQL query with filters for search.
        """

        variables = {
            "page": page,
            "perPage": per_page,
            "type": media_type,
            "sort": [sort],
            "search": search,
        }

        if season:
            variables["season"] = season
        if season_year:
            variables["seasonYear"] = season_year
        if format:
            variables["format"] = format
        if status:
            variables["status"] = status
        if genre_in:
            variables["genreIn"] = genre_in
        if tag_in:
            variables["tagIn"] = tag_in
        if is_adult:
            variables["isAdult"] = is_adult
        if country_of_origin:
            variables["countryOfOrigin"] = country_of_origin

        graphql_query = {
            "query": """ 
            query($page: Int, $perPage: Int, $type: MediaType, $sort: [MediaSort], $season: MediaSeason, $seasonYear: Int, $format: MediaFormat, $status: MediaStatus, $genreIn: [String], $tagIn: [String], $search: String, $isAdult: Boolean, $countryOfOrigin: CountryCode) {
              Page(page: $page, perPage: $perPage) {
                pageInfo {
                  currentPage
                  hasNextPage
                  perPage
                  total
                }
                media(type: $type, sort: $sort, season: $season, seasonYear: $seasonYear, format: $format, status: $status, genre_in: $genreIn, tag_in: $tagIn, search: $search, isAdult: $isAdult, countryOfOrigin: $countryOfOrigin) {
                  id
                  title {
                    english
                    romaji
                  }
                  format
                  genres
                  episodes
                  duration
                  status
                  nextAiringEpisode {
                    episode
                    airingAt
                    timeUntilAiring
                  }
                  studios {
                    edges {
                      isMain
                      node {
                        id
                        name
                      }
                    }
                  }
                  coverImage {
                    large
                  }
                  season
                  seasonYear
                  averageScore
                  chapters
                  startDate {
                    year
                    day
                    month
                  }
                  endDate {
                    year
                    month
                    day
                  }
                }
              }
            }
            """,
            "variables": variables,
        }

        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="search_media",
        )

        page_data = data.get("data", {}).get("Page", {})
        media_list = page_data.get("media", [])

        page_info = AnilistPageInfo.model_validate(page_data.get("pageInfo", {}))

        search_media = []
        for media in media_list:
            media["main_studio"] = self.extract_main_studio(media.get("studios"))
            search_media.append(AnilistMediaMinimal.model_validate(media))

       

        return search_media, page_info

    async def get_media_detail(self, media_id: int) -> AnilistMediaDetailed:
        """
        Fetches detailed information for a specific media by ID.
        Uses the provided GraphQL query.
        """

        variables = {"mediaId": media_id}

        graphql_query = {
            "query": """
            query($mediaId: Int) {
              Media(id: $mediaId) {
                averageScore
                bannerImage
                chapters
                countryOfOrigin
                coverImage {
                  medium
                  large
                }
                description
                duration
                endDate {
                  day
                  month
                  year
                }
                episodes
                format
                genres
                isAdult
                nextAiringEpisode {
                  episode
                  airingAt
                  timeUntilAiring
                }
                relations {
                  edges {
                    relationType
                    node {
                      title {
                        english
                        romaji
                      }
                      format
                      id
                      status
                    }
                  }
                }
                season
                seasonYear
                source
                startDate {
                  day
                  month
                  year
                }
                status
                synonyms
                title {
                  english
                  native
                  romaji
                }
                type
                volumes
                tags {
                  name
                  isMediaSpoiler
                  isGeneralSpoiler
                  rank
                }
                studios {
                  edges {
                    isMain
                    node {
                      name
                      id
                    }
                  }
                }
                id
              }
            }
            """,
            "variables": variables,
        }

       
        data = await perform_request(
            client=self.client,
            method="POST",
            url=ANILIST_URL,
            headers=None,
            params=None,
            graphql_query=graphql_query,
            action="get_media_detail",
        )

        media = data.get("data", {}).get("Media", {})

        detailed_media = AnilistMediaDetailed.model_validate(media)


        return detailed_media
