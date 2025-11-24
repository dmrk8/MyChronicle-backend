from typing import Any, List, Optional, Tuple, Dict
import httpx
import asyncio
import logging

from app.models.anilist_models import AnilistMedia, AnilistMediaMinimal, AnilistPageInfo

ANILIST_URL = "https://graphql.anilist.co"

logger = logging.getLogger(__name__)

class AnilistApi:
    def __init__(self):
        pass
    
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
        media_type: str
    ) -> List[AnilistMediaMinimal]:
        """
        Fetches featured media data: all time popular, trending now, popular this season, and upcoming next season.
        Uses the provided GraphQL query with different parameters for each category.
        """
        
        variables = {
            "page": page,
            "perPage": per_page,
            "sort": [sort],
            "type": media_type
            }
        
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
            "variables": variables
        }

        try:
            logger.info(f"Sending GraphQL request to Anilist: variables={variables}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(ANILIST_URL, json=graphql_query)
                response.raise_for_status()
                data = response.json()
                
                if "errors" in data:
                    logger.error("AniList GraphQL error: %s", data["errors"])
                    raise Exception(f"AniList error: {data['errors']}")
            
                # Extract media data from the response
                media_list = data.get("data", {}).get("Page", {}).get("media", [])
                
                # Map each media item to AnilistMedia model using model_validate
                featured_media = []
                for media in media_list:
                    # Extract main studio
                    media["main_studio"] = self.extract_main_studio(media.get("studios"))
                    # Get the large cover image
                    media["coverImageLarge"] = media.get("coverImage", {}).get("large")
                    
                    featured_media.append(AnilistMediaMinimal.model_validate(media))      
                
                logger.info(f"Successfully fetched {len(featured_media)} featured media items")
                return featured_media
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching featured media: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error while fetching featured media: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error while fetching featured media: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching featured media: {str(e)}")
            raise
    
    async def search_media(
        self,
        page: int,
        per_page: int,
        search: Optional[str],
        media_type: str,
        sort: str,
        season: Optional[str] = None,
        season_year: Optional[int] = None,
        format: Optional[str] = None,
        status: Optional[str] = None,
        genre_in: Optional[List[str]] = None,
        tag_in: Optional[List[str]] = None
    ) -> tuple[List[AnilistMediaMinimal], AnilistPageInfo]:
        """
        Searches for media based on the provided parameters.
        Uses the provided GraphQL query with filters for search.
        """
        
        variables = {
            "page": page,
            "perPage": per_page,
            "type": media_type,
            "sort": [sort]
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
            
        graphql_query = { 
            "query": """ 
            query($page: Int, $perPage: Int, $type: MediaType, $sort: [MediaSort], $season: MediaSeason, $seasonYear: Int, $format: MediaFormat, $status: MediaStatus, $genreIn: [String], $tagIn: [String], $search: String) {
              Page(page: $page, perPage: $perPage) {
                pageInfo {
                  currentPage
                  hasNextPage
                  perPage
                  total
                }
                media(type: $type, sort: $sort, season: $season, seasonYear: $seasonYear, format: $format, status: $status, genre_in: $genreIn, tag_in: $tagIn, $search: String) {
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
            "variables": variables
        }

        try:
            logger.info(f"Sending GraphQL search request to Anilist: variables={variables}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(ANILIST_URL, json=graphql_query)
                response.raise_for_status()
                data = response.json()
                
                if "errors" in data:
                    logger.error("AniList GraphQL error: %s", data["errors"])
                    raise Exception(f"AniList error: {data['errors']}")
            
                # Extract media data and page info from the response
                page_data = data.get("data", {}).get("Page", {})
                media_list = page_data.get("media", [])
                
                page_info = AnilistPageInfo.model_validate(page_data.get("pageInfo", {}))
                
                # Map each media item to AnilistMediaMinimal model using model_validate
                search_media = []
                for media in media_list:
                    # Extract main studio
                    media["main_studio"] = self.extract_main_studio(media.get("studios"))
                    # Get the large cover image
                    media["coverImageLarge"] = media.get("coverImage", {}).get("large")
                    
                    search_media.append(AnilistMediaMinimal.model_validate(media))      
                
                logger.info(f"Successfully fetched {len(search_media)} search media items")
                return search_media, page_info 
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while searching media: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error while searching media: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error while searching media: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while searching media: {str(e)}")
            raise
    
    def browse_media(self):
        pass















