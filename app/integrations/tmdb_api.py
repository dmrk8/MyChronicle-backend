from typing import List, Optional
import httpx
from dotenv import load_dotenv
import os
import logging
import asyncio
from app.models.tmdb_models import TMDBMediaMinimal, TMDBPageInfo, TMDBMediaDetail 
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

    async def get_discover_media(
        self,
        media_type: str,  # "movie" or "tv"
        page: int,
        language: str,
        sort_by: str,
        primary_release_date_gte: Optional[str] = None,  # For movies
        primary_release_date_lte: Optional[str] = None,  # For movies
        air_date_gte: Optional[str] = None,  # For TV
        air_date_lte: Optional[str] = None,  # For TV
        first_air_date_gte: Optional[str] = None,  # For TV
        first_air_date_lte: Optional[str] = None,  # For TV
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
        with_status: Optional[str] = None,  # 3 ended, 4 canceled, 5 returning series
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches discovered media (movie or TV) with filters from TMDB.
        """
        base_url = f"{self.BASE_URL}/discover/{media_type}?"
        params = {
            "language": language,
            "page": page,
            "sort_by": sort_by,
            "include_adult": "false",
            "without_keywords": "210024",
        }

        # Add date params only if provided
        if primary_release_date_gte:
            params["primary_release_date.gte"] = primary_release_date_gte
        if primary_release_date_lte:
            params["primary_release_date.lte"] = primary_release_date_lte
        if air_date_gte:
            params["air_date.gte"] = air_date_gte
        if air_date_lte:
            params["air_date.lte"] = air_date_lte
        if first_air_date_gte:
            params["first_air_date.gte"] = first_air_date_gte
        if first_air_date_lte:
            params["first_air_date.lte"] = first_air_date_lte

        if media_type == "movie":
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

        # Build URL with params
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = base_url + query_string

        try:
            logger.info(
                f"Fetching discover {media_type}: page={page}, language={language}, sort_by={sort_by}, primary_release_date_gte={primary_release_date_gte}, primary_release_date_lte={primary_release_date_lte}, air_date_gte={air_date_gte}, air_date_lte={air_date_lte}, first_air_date_gte={first_air_date_gte}, first_air_date_lte={first_air_date_lte}, with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}, with_status={with_status}"
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

    async def get_media_detail(
        self,
        media_type: str,  # "movie" or "tv"
        media_id: int,
        language: str,
    ) -> TMDBMediaDetail:
        """
        Fetches detailed information for a specific movie or TV show from TMDB, including keywords.
        """
        url = f"{self.BASE_URL}/{media_type}/{media_id}?append_to_response=keywords&language={language}"

        try:
            logger.info(
                f"Fetching media detail: media_type={media_type}, media_id={media_id}, language={language}"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.HEADERS)
                response.raise_for_status()
                data = response.json()

                # Validate and return TMDBMediaDetail
                media_detail = TMDBMediaDetail.model_validate(data)

                logger.info(f"Successfully fetched media detail for {media_type} {media_id}")
                return media_detail

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching media detail: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching media detail: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing or validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching media detail: {str(e)}")
            raise

    
