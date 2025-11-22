import logging
from typing import Optional
from app.integrations.tmdb_api import TMDBApi
from app.models.tmdb_models import TMDBPagination

logger = logging.getLogger(__name__)

class TMDBService:
    def __init__(self):
        self.api = TMDBApi()

    async def search_movies(
        self,
        query: str,
        page: int,
        language: str,
        include_adult: bool
    ) -> Optional[TMDBPagination]:
        """
        Service method to search for movies using TMDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating movie search for '{query}' on page {page}")
            result = await self.api.search_movie(
                page=page,
                query=query,
                language=language,
                include_adult=include_adult
            )
            logger.info(f"Service: Successfully retrieved {len(result.results)} movies")
            return result
        except Exception as e:
            logger.error(f"Service: Failed to search movies for '{query}': {e}")
            return None  # Or raise custom exception