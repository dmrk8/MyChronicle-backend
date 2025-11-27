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

    async def get_popular_season(
        self,
        media_type: str,
        start_date: str,
        end_date: str,
        page: int,
        language: str,
        sort_by: str,
    ) -> TMDBPagination:
        """
        Service method to get popular season media using TMDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(
                f"Service: Initiating popular season {media_type} fetch for start_date {start_date}, end_date {end_date} on page {page}"
            )
            results, page_info = await self.api.get_popular_season(
                media_type=media_type,
                start_date=start_date,
                end_date=end_date,
                page=page,
                language=language,
                sort_by=sort_by,
            )
            result = TMDBPagination(
                results=results,
                page=page_info.page,
                total_pages=page_info.total_pages,  # type: ignore
                total_results=page_info.total_results,  # type: ignore
            )
            logger.info(
                f"Service: Successfully retrieved {len(result.results)} popular season {media_type} items"
            )
            return result
        except Exception as e:
            logger.error(f"Service: Failed to get popular season {media_type}: {e}")
            raise

    async def get_discover_media(
        self,
        media_type: str,
        page: int,
        language: str,
        sort_by: str,
        primary_release_date_gte: Optional[str] = None,
        primary_release_date_lte: Optional[str] = None,
        air_date_gte: Optional[str] = None,
        air_date_lte: Optional[str] = None,
        first_air_date_gte: Optional[str] = None,
        first_air_date_lte: Optional[str] = None,
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
        with_status: Optional[str] = None,  # For TV: status filter
    ) -> Optional[TMDBPagination]:
        """
        Service method to get discovered media using TMDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating discover {media_type} fetch for page {page}")
            results, page_info = await self.api.get_discover_media(
                media_type=media_type,
                page=page,
                language=language,
                sort_by=sort_by,
                primary_release_date_gte=primary_release_date_gte,
                primary_release_date_lte=primary_release_date_lte,
                air_date_gte=air_date_gte,
                air_date_lte=air_date_lte,
                first_air_date_gte=first_air_date_gte,
                first_air_date_lte=first_air_date_lte,
                with_genres=with_genres,
                with_keywords=with_keywords,
                with_runtime_gte=with_runtime_gte,
                with_runtime_lte=with_runtime_lte,
                with_original_language=with_original_language,
                with_status=with_status,
            )
            result = TMDBPagination(
                results=results,
                page=page_info.page,
                total_pages=page_info.total_pages,  # type: ignore
                total_results=page_info.total_results,  # type: ignore
            )
            logger.info(
                f"Service: Successfully retrieved {len(result.results)} discover {media_type} items"
            )
            return result
        except Exception as e:
            logger.error(f"Service: Failed to get discover {media_type}: {e}")
            raise
