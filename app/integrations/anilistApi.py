from typing import Any, List, Optional, Tuple, Dict
import httpx
import asyncio

from app.models.anilist_models import AnilistMedia, AnilistMediaMinimal

ANILIST_URL = "https://graphql.anilist.co"

class AnilistApi:
    def __init__(self):
        pass
    
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

        async with httpx.AsyncClient() as client:
            response = await client.post(ANILIST_URL, json=graphql_query)
            response.raise_for_status()
            data = response.json()
            
            # Extract media data from the response
            media_list = data.get("data", {}).get("Page", {}).get("media", [])
            
            # Map each media item to AnilistMedia model using model_validate
            featured_media = [AnilistMediaMinimal.model_validate(media) for media in media_list]
            
            return featured_media
            
            
    
    def browse_media(self):
        pass
    
    def search_media(self):
        pass















