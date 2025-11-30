import logging
from typing import Optional, List, Union
from app.integrations.tmdb_api import TMDBApi
from app.models.tmdb_models import (
    TMDBPagination,
    TMDBMovieDetail,
    TMDBTVDetail,
    TMDBMediaMinimal,
    TMDBPageInfo,
)
from app.services.imdb_service import IMDBService

logger = logging.getLogger(__name__)


class TMDBService:
    def __init__(self):
        self.api = TMDBApi()
        self.imdb_service = IMDBService()

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

    async def get_movie_detail(
        self,
        movie_id: int,
        language: str,
    ) -> TMDBMovieDetail:
        """
        Service method to get movie detail using TMDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating movie detail fetch for {movie_id}")
            result = await self.api.get_movie_detail(movie_id, language)
            if result.imdb_id is not None:
                rating = await self.imdb_service.get_imdb_rating(result.imdb_id)
                result.imdb_rating_count = rating.rating_count
                result.imdb_rating_value = rating.rating_value
            else:
                logger.info("IMDB ID is empty")
            logger.info(f"Service: Successfully retrieved movie detail for {movie_id}")
            return result
        except Exception as e:
            logger.error(f"Service: Failed to get movie detail for {movie_id}: {e}")
            raise

    async def get_tv_detail(
        self,
        tv_id: int,
        language: str,
    ) -> TMDBTVDetail:
        """
        Service method to get TV detail using TMDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating TV detail fetch for {tv_id}")
            result = await self.api.get_tv_detail(tv_id, language)
            if result.imdb_id is not None:
                rating = await self.imdb_service.get_imdb_rating(result.imdb_id)
                result.imdb_rating_count = rating.rating_count
                result.imdb_rating_value = rating.rating_value
            else:
                logger.info("IMDB ID is empty")
            logger.info(f"Service: Successfully retrieved TV detail for {tv_id}")
            return result
        except Exception as e:
            logger.error(f"Service: Failed to get TV detail for {tv_id}: {e}")
            raise

    async def search_movie(
        self,
        page: int,
        sort_by: str,
        language: str,
        search: str,
        genres: List[int],  # list of genre ids
        keywords: List[int],  # list of keyword ids
        length_lte: int,
        length_gte: int,
        primary_release_date_gte: Optional[str] = None,  # For movies
        primary_release_date_lte: Optional[str] = None,  # For movies
        with_original_language: Optional[str] = None,
    ):

        
        pass
