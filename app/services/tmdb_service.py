import logging
from typing import Optional
from app.integrations.tmdb_api import TMDBApi
from app.models.tmdb_models import TMDBPagination

logger = logging.getLogger(__name__)


class TMDBService:
    def __init__(self):
        self.api = TMDBApi()

    # ... existing code ...

    # async def search_movies(
    #     self, query: str, page: int, language: str, include_adult: bool
    # ) -> Optional[TMDBPagination]:
    #     """
    #     Service method to search for movies using TMDB API.
    #     Handles business logic, logging, and error handling.
    #     """
    #     try:
    #         logger.info(f"Service: Initiating movie search for '{query}' on page {page}")
    #         result = await self.api.search_movie(
    #             page=page, query=query, language=language, include_adult=include_adult
    #         )
    #         logger.info(f"Service: Successfully retrieved {len(result.results)} movies")
    #         return result
    #     except Exception as e:
    #         logger.error(f"Service: Failed to search movies for '{query}': {e}")
    #         return None  # Or raise custom exception

    async def get_trending_media(
        self, media_type: str, time_window: str, language: str, page: int
    ) -> TMDBPagination:
        """
        Service method to get trending media using TMDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(
                f"Service: Initiating trending {media_type} fetch for time_window {time_window} on page {page}"
            )
            results, page_info = await self.api.get_trending_media(
                media_type=media_type, time_window=time_window, language=language, page=page
            )
            result = TMDBPagination(
                results=results,
                page=page_info.page,
                total_pages=page_info.total_pages,  # type: ignore
                total_results=page_info.total_results,  # type: ignore
            )
            logger.info(
                f"Service: Successfully retrieved {len(result.results)} trending {media_type} items"
            )
            return result
        except Exception as e:
            logger.error(f"Service: Failed to get trending {media_type}: {e}")
            raise
