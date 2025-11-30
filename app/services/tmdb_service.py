import asyncio
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

    async def search_movie_test(
        self,
        page: int,
        sort_by: str,  # Now expects enum value like "POPULARITY_DESC"
        language: str,
        search: str,
        genres: List[int],  # list of genre ids
        keywords: List[int],  # list of keyword ids
        length_lte: int,
        length_gte: int,
        release_date_gte: Optional[str] = None,
        release_date_lte: Optional[str] = None,
        with_original_language: Optional[str] = None,
    ) -> TMDBPagination:
        """
        Service method to search and filter movies.
        """
        try:
            logger.info(f"Service: Initiating movie search for query '{search}' on page {page}")

            if search:
                results, page_info = await self.api.search_movies(
                    query=search, page=page, language=language
                )

                media_ids = [media.id for media in results]

                detailed_results = await self.get_bulk_movie_details(media_ids, language)

                filtered_results = detailed_results

                if genres:
                    genre_set = set(genres)
                    # Keep media that have all requested genres (but may have others)
                    filtered_results = [
                        media
                        for media in filtered_results
                        if genre_set.issubset(set(genre.id for genre in media.genres))
                    ]

                if keywords:
                    keywords_set = set(keywords)
                    excluded_keyword = 210024  # anime

                    # Keep media that have all requested keywords (but may have others)
                    filtered_results = [
                        media
                        for media in filtered_results
                        if media.keywords
                        and keywords_set.issubset(
                            media_keywords := {keyword.id for keyword in media.keywords.keywords}
                        )
                        and excluded_keyword not in media_keywords
                    ]

                if length_lte or length_gte:
                    filtered_results = [
                        media
                        for media in filtered_results
                        if media.runtime is not None and length_gte <= media.runtime <= length_lte
                    ]

                if release_date_gte or release_date_lte:
                    filtered_results = [
                        media
                        for media in filtered_results
                        if media.release_date is not None
                        and (release_date_gte is None or media.release_date >= release_date_gte)
                        and (release_date_lte is None or media.release_date <= release_date_lte)
                    ]

                if with_original_language:
                    filtered_results = [
                        media
                        for media in filtered_results
                        if media.original_language == with_original_language
                    ]

                if sort_by:
                    if sort_by == "POPULARITY_DESC":
                        filtered_results.sort(key=lambda x: x.popularity, reverse=True)
                    elif sort_by == "IMDB_DESC":
                        filtered_results.sort(key=lambda x: x.imdb_rating_value or 0, reverse=True)

                # Convert filtered results to TMDBMediaMinimal
                results = [
                    TMDBMediaMinimal.model_validate(media.model_dump())
                    for media in filtered_results
                ]
                result = TMDBPagination(
                    results=results,
                    page=page,
                    total_pages=page_info.total_pages,  # type: ignore
                    total_results=len(filtered_results),  # Approximate # type: ignore
                )
                logger.info(
                    f"Service: Successfully retrieved {len(result.results)} filtered movie results"
                )
                return result
            else:
                return TMDBPagination(results=[], page=page, total_pages=1, total_results=0)  # type: ignore
        except Exception as e:
            logger.error(f"Service: Failed to search movies: {e}")
            raise

    async def get_bulk_movie_details(
        self,
        movie_ids: List[int],
        language: str,
    ) -> List[TMDBMovieDetail]:
        """
        Service method to get bulk movie details.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating bulk movie details fetch for {len(movie_ids)} movies")
            results = await self.api.get_bulk_movie_details(movie_ids, language)

            logger.info(
                f"Service: Successfully retrieved bulk movie details for {len(results)} movies"
            )
            return results
        except Exception as e:
            logger.error(f"Service: Failed to get bulk movie details: {e}")
            raise

    async def get_bulk_tv_details(
        self,
        tv_ids: List[int],
        language: str,
    ) -> List[TMDBTVDetail]:
        """
        Service method to get bulk TV details.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating bulk TV details fetch for {len(tv_ids)} TV shows")
            results = await self.api.get_bulk_tv_details(tv_ids, language)

            # Concurrently fetch IMDB ratings
            imdb_tasks = []
            for result in results:
                if result.imdb_id is not None:
                    imdb_tasks.append(self.imdb_service.get_imdb_rating(result.imdb_id))
                else:
                    imdb_tasks.append(None)  # Placeholder

            imdb_ratings = await asyncio.gather(*imdb_tasks, return_exceptions=True)

            for i, result in enumerate(results):
                rating = imdb_ratings[i]
                if isinstance(rating, Exception):
                    logger.warning(f"Failed to get IMDB rating for TV {result.id}: {rating}")
                elif rating is not None:
                    result.imdb_rating_count = rating.rating_count
                    result.imdb_rating_value = rating.rating_value
                else:
                    logger.info(f"IMDB ID is empty for TV {result.id}")

            logger.info(
                f"Service: Successfully retrieved bulk TV details for {len(results)} TV shows"
            )
            return results
        except Exception as e:
            logger.error(f"Service: Failed to get bulk TV details: {e}")
            raise
