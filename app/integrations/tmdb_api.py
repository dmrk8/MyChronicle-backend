from typing import List, Optional
import httpx
from dotenv import load_dotenv
import os
import logging
import asyncio
from app.models.tmdb_models import (
    TMDBMediaMinimal,
    TMDBPageInfo,
    TMDBMovieDetail,
    TMDBTVDetail,
    TMDBExternalIds,
)

load_dotenv()

logger = logging.getLogger(__name__)


class TMDBApi:
    BASE_URL = "https://api.themoviedb.org/3"

    @property
    def HEADERS(self):
        token = os.getenv("TMDB_ACCESS_TOKEN")
        return {"accept": "application/json", "Authorization": f"Bearer {token}"}

    async def get_trending_media(
        self,
        media_type: str,  # "movie" or "tv"
        time_window: str,  # "day" or "week"
        language: str,
        page: int = 1,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches trending media (movie or TV) from TMDB.
        """
        url = f"{self.BASE_URL}/trending/{media_type}/{time_window}?language={language}&page={page}"

        try:
            logger.info(
                f"Fetching trending {media_type}: time_window={time_window}, page={page}, language={language}"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Map results to TMDBMediaMinimal
                results = [
                    TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])
                ]

                page_info = TMDBPageInfo.model_validate(
                    {
                        "page": data.get("page", page),
                        "total_pages": data.get("total_pages", 1),
                        "total_results": data.get("total_results", 0),
                    }
                )

                logger.info(f"Successfully fetched {len(results)} trending {media_type} items")
                return results, page_info

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching trending media: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching trending media: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching trending media: {str(e)}")
            raise

    async def get_search_movie(
        self,
        page: int,
        query: str,
        language: str = "en-US",
        include_adult: bool = False,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Searches for movies on TMDB.
        """
        url = f"{self.BASE_URL}/search/movie"
        params = {
            "query": query,
            "language": language,
            "page": page,
            "include_adult": str(include_adult).lower(),
        }

        try:
            logger.info(
                f"Searching movies for query: '{query}', page: {page}, language: {language}, include_adult: {include_adult}"
            )
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.HEADERS, params=params)
                response.raise_for_status()
                data = response.json()

                results = [
                    TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])
                ]
                page_info = TMDBPageInfo.model_validate(
                    {
                        "page": data.get("page", page),
                        "total_pages": data.get("total_pages", 1),
                        "total_results": data.get("total_results", 0),
                    }
                )
                logger.info(
                    f"Successfully retrieved {len(results)} movies from page {data.get('page', 1)} of {data.get('total_pages', 1)}"
                )
                return results, page_info

        except Exception as e:
            logger.error(f"Error searching movies for query '{query}': {e}")
            raise ValueError(f"Invalid API response: {e}")

    async def get_search_tv(
        self,
        page: int,
        query: str,
        language: str = "en-US",
        include_adult: bool = False,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Searches for TV shows on TMDB.
        """
        url = f"{self.BASE_URL}/search/tv"
        params = {
            "query": query,
            "language": language,
            "page": page,
            "include_adult": str(include_adult).lower(),
        }

        try:
            logger.info(
                f"Searching TV shows for query: '{query}', page: {page}, language: {language}, include_adult: {include_adult}"
            )
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.HEADERS, params=params)
                response.raise_for_status()
                data = response.json()

                results = [
                    TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])
                ]
                page_info = TMDBPageInfo.model_validate(
                    {
                        "page": data.get("page", page),
                        "total_pages": data.get("total_pages", 1),
                        "total_results": data.get("total_results", 0),
                    }
                )
                logger.info(
                    f"Successfully retrieved {len(results)} TV shows from page {data.get('page', 1)} of {data.get('total_pages', 1)}"
                )
                return results, page_info

        except Exception as e:
            logger.error(f"Error searching TV shows for query '{query}': {e}")
            raise ValueError(f"Invalid API response: {e}")

    async def get_popular_season(
        self,
        media_type: str,  # "movie" or "tv"
        start_date: str,  # e.g., "2025-08-26"
        end_date: str,  # e.g., "2025-11-26"
        page: int,
        language: str,
        sort_by: str,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches popular movies in a specific season (date range) from TMDB.
        """

        date_param = "primary_release_date" if media_type == "movie" else "air_date"
        url = f"{self.BASE_URL}/discover/{media_type}?sort_by={sort_by}&{date_param}.gte={start_date}&{date_param}.lte={end_date}&without_keywords=210024&language={language}&page={page}"

        try:
            logger.info(
                f"Fetching popular season movies: start_date={start_date}, end_date={end_date}, page={page}, language={language}, sort_by={sort_by}"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Map results to TMDBMediaMinimal
                results = [
                    TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])
                ]

                page_info = TMDBPageInfo.model_validate(
                    {
                        "page": data.get("page", 1),
                        "total_pages": data.get("total_pages", 1),
                        "total_results": data.get("total_results", 0),
                    }
                )

                logger.info(f"Successfully fetched {len(results)} popular season movies")
                return results, page_info

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching popular season movies: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching popular season movies: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching popular season movies: {str(e)}")
            raise

    async def get_discover_movie(
        self,
        page: int,
        language: str,
        sort_by: str,
        primary_release_date_gte: Optional[str] = None,  # For movies
        primary_release_date_lte: Optional[str] = None,  # For movies
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
        without_genres: Optional[str] = None,
        without_keywords: Optional[str] = None,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches discovered movies with filters from TMDB.
        """
        base_url = f"{self.BASE_URL}/discover/movie?"
        params = {
            "language": language,
            "page": page,
            "sort_by": sort_by,
            "include_adult": "false"
        }

        if primary_release_date_gte:
            params["primary_release_date.gte"] = primary_release_date_gte
        if primary_release_date_lte:
            params["primary_release_date.lte"] = primary_release_date_lte
        if with_genres:
            params["with_genres"] = with_genres
        if with_keywords:
            params["with_keywords"] = with_keywords
        if with_runtime_gte is not None:
            params["with_runtime.gte"] = str(with_runtime_gte)
        if with_runtime_lte is not None:
            params["with_runtime.lte"] = str(with_runtime_lte)
        if with_original_language:
            params["with_original_language"] = with_original_language
        if without_genres:
            params["without_genres"] = without_genres
        if without_keywords:
            params["without_keywords"] = without_keywords

        # Build URL with params
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = base_url + query_string

        try:
            logger.info(
                f"Fetching discover movie: page={page}, language={language}, sort_by={sort_by}, primary_release_date_gte={primary_release_date_gte}, primary_release_date_lte={primary_release_date_lte}, with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}, without_genres={without_genres}, without_keywords={without_keywords}"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Map results to TMDBMediaMinimal
                results = [
                    TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])
                ]

                page_info = TMDBPageInfo.model_validate(
                    {
                        "page": data.get("page", page),
                        "total_pages": data.get("total_pages", 1),
                        "total_results": data.get("total_results", 0),
                    }
                )

                logger.info(f"Successfully fetched {len(results)} discover movie items")
                return results, page_info

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching discover movie: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching discover movie: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching discover movie: {str(e)}")
            raise

    async def get_discover_tv(
        self,
        page: int,
        language: str,
        sort_by: str,
        air_date_gte: Optional[str] = None,
        air_date_lte: Optional[str] = None,
        first_air_date_gte: Optional[str] = None,
        first_air_date_lte: Optional[str] = None,
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
        with_status: Optional[str] = None,  # 3 ended, 4 canceled, 5 returning series
        without_genres: Optional[str] = None,
        without_keywords: Optional[str] = None,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches discovered TV shows with filters from TMDB.
        """
        base_url = f"{self.BASE_URL}/discover/tv?"
        params = {
            "language": language,
            "page": page,
            "sort_by": sort_by,
            "include_adult": "false",
        }

        # Add date params only if provided
        if air_date_gte:
            params["air_date.gte"] = air_date_gte
        if air_date_lte:
            params["air_date.lte"] = air_date_lte
        if first_air_date_gte:
            params["first_air_date.gte"] = first_air_date_gte
        if first_air_date_lte:
            params["first_air_date.lte"] = first_air_date_lte
        if with_genres:
            params["with_genres"] = with_genres
        if with_keywords:
            params["with_keywords"] = with_keywords
        if with_runtime_gte is not None:
            params["with_runtime.gte"] = str(with_runtime_gte)
        if with_runtime_lte is not None:
            params["with_runtime.lte"] = str(with_runtime_lte)
        if with_original_language:
            params["with_original_language"] = with_original_language
        if with_status:
            params["with_status"] = with_status
        if without_genres:
            params["without_genres"] = without_genres
        if without_keywords:
            params["without_keywords"] = without_keywords

        # Build URL with params
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = base_url + query_string

        try:
            logger.info(
                f"Fetching discover tv: page={page}, language={language}, sort_by={sort_by}, air_date_gte={air_date_gte}, air_date_lte={air_date_lte}, first_air_date_gte={first_air_date_gte}, first_air_date_lte={first_air_date_lte}, with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}, with_status={with_status}, without_genres={without_genres}, without_keywords={without_keywords}"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Map results to TMDBMediaMinimal
                results = [
                    TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])
                ]

                page_info = TMDBPageInfo.model_validate(
                    {
                        "page": data.get("page", page),
                        "total_pages": data.get("total_pages", 1),
                        "total_results": data.get("total_results", 0),
                    }
                )

                logger.info(f"Successfully fetched {len(results)} discover tv items")
                return results, page_info

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching discover tv: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching discover tv: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching discover tv: {str(e)}")
            raise

    async def get_movie_detail(
        self,
        movie_id: int,
        language: str,
    ) -> TMDBMovieDetail:
        """
        Fetches detailed information for a specific movie from TMDB, including keywords.
        """
        url = f"{self.BASE_URL}/movie/{movie_id}?append_to_response=keywords&language={language}"

        try:
            logger.info(f"Fetching movie detail: movie_id={movie_id}, language={language}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Validate and return TMDBMovieDetail
                movie_detail = TMDBMovieDetail.model_validate(data)

                logger.info(f"Successfully fetched movie detail for {movie_id}")
                return movie_detail

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching movie detail: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching movie detail: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching movie detail: {str(e)}")
            raise

    async def get_tv_detail(
        self,
        tv_id: int,
        language: str,
    ) -> TMDBTVDetail:
        """
        Fetches detailed information for a specific TV show from TMDB, including keywords.
        """
        url = f"{self.BASE_URL}/tv/{tv_id}?append_to_response=keywords,external_ids&language={language}"

        try:
            logger.info(f"Fetching TV detail: tv_id={tv_id}, language={language}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Validate and return TMDBTVDetail
                tv_detail = TMDBTVDetail.model_validate(data)

                logger.info(f"Successfully fetched TV detail for {tv_id}")
                return tv_detail

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching TV detail: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching TV detail: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching TV detail: {str(e)}")
            raise

    async def get_bulk_movie_details(
        self,
        movie_ids: List[int],
        language: str = "en-US",
    ) -> List[TMDBMovieDetail]:
        """
        Fetches detailed information for multiple movies concurrently from TMDB, including keywords.
        """
        try:
            logger.info(f"Fetching bulk movie details: movie_ids={movie_ids}, language={language}")

            # Create tasks for concurrent fetching
            tasks = [self.get_movie_detail(movie_id, language) for movie_id in movie_ids]

            # Gather results, allowing exceptions to be handled
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and collect successful results
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch movie detail for {movie_ids[i]}: {str(result)}")
                else:
                    successful_results.append(result)

            logger.info(
                f"Successfully fetched {len(successful_results)} out of {len(movie_ids)} bulk movie details"
            )
            return successful_results

        except Exception as e:
            logger.error(f"Unexpected error fetching bulk movie details: {str(e)}")
            raise

    async def get_bulk_tv_details(
        self,
        tv_ids: List[int],
        language: str = "en-US",
    ) -> List[TMDBTVDetail]:
        """
        Fetches detailed information for multiple TV shows concurrently from TMDB, including keywords.
        """
        try:
            logger.info(f"Fetching bulk TV details: tv_ids={tv_ids}, language={language}")

            # Create tasks for concurrent fetching
            tasks = [self.get_tv_detail(tv_id, language) for tv_id in tv_ids]

            # Gather results, allowing exceptions to be handled
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and collect successful results
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch TV detail for {tv_ids[i]}: {str(result)}")
                else:
                    successful_results.append(result)

            logger.info(
                f"Successfully fetched {len(successful_results)} out of {len(tv_ids)} bulk TV details"
            )
            return successful_results

        except Exception as e:
            logger.error(f"Unexpected error fetching bulk TV details: {str(e)}")
            raise
