from typing import List, Optional
import httpx
from dotenv import load_dotenv
import os
import logging
from app.models.tmdb_models import TMDBMediaMinimal, TMDBPageInfo

load_dotenv()

logger = logging.getLogger(__name__)


class TMDBApi:
    BASE_URL = "https://api.themoviedb.org/3/search/movie"

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
        url = f"https://api.themoviedb.org/3/trending/{media_type}/{time_window}?language={language}&page={page}"

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

    # async def search_movie(
    #     self,
    #     page: int,
    #     query: str,
    #     language: str = "en-US",  # language of the query results
    #     include_adult: bool = False,  # amateur porn like JAVs
    # ) -> TMDBPagination:
    #     logger.info(
    #         f"Searching movies for query: '{query}', page: {page}, language: {language}, include_adult: {include_adult}"
    #     )
    #     params = {
    #         "query": query,
    #         "language": language,
    #         "page": page,
    #         "include_adult": str(include_adult).lower(),
    #     }

    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(self.BASE_URL, headers=self.HEADERS, params=params)
    #         response.raise_for_status()
    #         try:
    #             data = response.json()
    #             movies = []
    #             for movie_data in data["results"]:
    #                 movies.append(self.map_movie_search_results(movie_data))

    #             logger.info(
    #                 f"Successfully retrieved {len(movies)} movies from page {data.get('page', 1)} of {data.get('total_pages', 1)}"
    #             )
    #             return TMDBPagination(
    #                 results=movies,
    #                 page=data.get("page", 1),
    #                 total_pages=data.get("total_pages", 1),
    #                 total_results=data.get("total_results", 0),
    #             )
    #         except Exception as e:
    #             logger.error(f"Error processing API response for query '{query}': {e}")
    #             raise ValueError(f"Invalid API response: {e}")

    # def map_movie_search_results(self, data) -> TMDB_Search_Movie:
    #     return TMDB_Search_Movie.model_validate(data)

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
        url = f"https://api.themoviedb.org/3/discover/{media_type}?sort_by={sort_by}&{date_param}.gte={start_date}&{date_param}.lte={end_date}&without_keywords=210024&language={language}&page={page}"

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

    async def get_discover_media(
        self,
        media_type: str,  # "movie" or "tv"
        start_date: Optional[str],
        end_date: str,  # e.g., "2025-11-26"
        page: int,
        language: str,
        sort_by: str,
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches discovered media (movie or TV) with filters from TMDB.
        """
        base_url = f"https://api.themoviedb.org/3/discover/{media_type}?"
        params = {
            "language": language,
            "page": page,
            "sort_by": sort_by,
            "include_adult": "false",
            "without_keywords": "210024",
        }

        if media_type == "movie":
            if start_date:
                params["primary_release_date.gte"] = start_date
            params["primary_release_date.lte"] = end_date
            params["include_video"] = "false"
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
        elif media_type == "tv":
            if start_date:
                params["air_date.gte"] = start_date
            params["air_date.lte"] = end_date
            params["first_air_date.gte"] = start_date
            params["first_air_date.lte"] = end_date
            params["include_null_first_air_dates"] = "false"
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

        # Build URL with params
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = base_url + query_string

        try:
            logger.info(
                f"Fetching discover {media_type}: start_date={start_date}, end_date={end_date}, page={page}, language={language}, sort_by={sort_by}, with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}"
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

                logger.info(f"Successfully fetched {len(results)} discover {media_type} items")
                return results, page_info

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching discover {media_type}: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching discover {media_type}: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching discover {media_type}: {str(e)}")
            raise
