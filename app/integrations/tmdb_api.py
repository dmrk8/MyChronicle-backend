from typing import List, Optional
import httpx
import structlog
import asyncio
from app.models.tmdb_models import (
    TMDBCollection,
    TMDBMediaMinimal,
    TMDBPageInfo,
    TMDBMovieDetail,
    TMDBTVDetail,
    TMDBExternalIds,
)
from app.integrations.http_helpers import perform_request


logger = structlog.get_logger().bind(api="TMDBApi")


class TMDBApi:
    def __init__(self, tmdb_access_token: str, client: httpx.AsyncClient):
        self.tmdb_access_token = tmdb_access_token
        self.BASE_URL = "https://api.themoviedb.org/3"
        self.client = client
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {tmdb_access_token}",
        }

    async def get_trending_media(
        self,
        media_type: str,  # "movie" or "tv"
        time_window: str,  # "day" or "week"
        language: str,
        page: int,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches trending media (movie or TV) from TMDB.
        """
        url = f"{self.BASE_URL}/trending/{media_type}/{time_window}"
        params = {"language": language, "page": page}
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            action="get_trending_media",
        )

        results = [TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])]

        page_info = TMDBPageInfo.model_validate(
            {
                "page": data.get("page", page),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            }
        )
        return results, page_info

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
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            action="get_search_movie",
        )

        results = [TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])]
        page_info = TMDBPageInfo.model_validate(
            {
                "page": data.get("page", page),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            }
        )
        return results, page_info

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
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            action="get_search_tv",
        )

        results = [TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])]
        page_info = TMDBPageInfo.model_validate(
            {
                "page": data.get("page", page),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            }
        )
        return results, page_info

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
        url = f"{self.BASE_URL}/discover/{media_type}"
        params = {
            "sort_by": sort_by,
            f"{date_param}.gte": start_date,
            f"{date_param}.lte": end_date,
            "without_keywords": "210024",
            "language": language,
            "page": page,
        }
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            
            action="get_popular_season",
        )

        results = [TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])]
        page_info = TMDBPageInfo.model_validate(
            {
                "page": data.get("page", 1),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            }
        )
        return results, page_info

    async def get_discover_movie(
        self,
        page: int,
        language: str,
        sort_by: str,
        primary_release_date_gte: Optional[str] = None,
        primary_release_date_lte: Optional[str] = None,
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
        url = f"{self.BASE_URL}/discover/movie"
        params = {"language": language, "page": page, "sort_by": sort_by, "include_adult": "false"}

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

        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            
            action="get_discover_movie",
        )

        results = [TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])]
        page_info = TMDBPageInfo.model_validate(
            {
                "page": data.get("page", page),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            }
        )
        return results, page_info

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
        with_status: Optional[str] = None,
        without_genres: Optional[str] = None,
        without_keywords: Optional[str] = None,
    ) -> tuple[List[TMDBMediaMinimal], TMDBPageInfo]:
        """
        Fetches discovered TV shows with filters from TMDB.
        """
        url = f"{self.BASE_URL}/discover/tv"
        params = {
            "language": language,
            "page": page,
            "sort_by": sort_by,
            "include_adult": "false",
        }

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

        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
           
            action="get_discover_tv",
        )

        results = [TMDBMediaMinimal.model_validate(item) for item in data.get("results", [])]
        page_info = TMDBPageInfo.model_validate(
            {
                "page": data.get("page", page),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            }
        )
        return results, page_info

    async def get_movie_detail(
        self,
        movie_id: int,
        language: str,
    ) -> TMDBMovieDetail:
        """
        Fetches detailed information for a specific movie from TMDB, including keywords.
        """
        url = f"{self.BASE_URL}/movie/{movie_id}"
        params = {
            "append_to_response": "keywords",
            "language": language,
        }
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            
            action="get_movie_detail",
        )

        movie_detail = TMDBMovieDetail.model_validate(data)
        return movie_detail

    async def get_tv_detail(
        self,
        tv_id: int,
        language: str,
    ) -> TMDBTVDetail:
        """
        Fetches detailed information for a specific TV show from TMDB, including keywords.
        """
        url = f"{self.BASE_URL}/tv/{tv_id}"
        params = {
            "append_to_response": "keywords,external_ids",
            "language": language,
        }
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            
            action="get_tv_detail",
        )

        tv_detail = TMDBTVDetail.model_validate(data)
        return tv_detail

    async def get_bulk_movie_details(
        self,
        movie_ids: List[int],
        language: str = "en-US",
    ) -> List[TMDBMovieDetail]:
        """
        Fetches detailed information for multiple movies concurrently from TMDB, including keywords.
        """
        tasks = [self.get_movie_detail(movie_id, language) for movie_id in movie_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Failed to fetch movie detail", movie_id=movie_ids[i])
            else:
                successful_results.append(result)
        logger.info(
            "bulk_movie_details_completed",
            len=len(successful_results),
            successful_results=len(movie_ids),
        )
        return successful_results

    async def get_bulk_tv_details(
        self,
        tv_ids: List[int],
        language: str = "en-US",
    ) -> List[TMDBTVDetail]:
        """
        Fetches detailed information for multiple TV shows concurrently from TMDB, including keywords.
        """
        tasks = [self.get_tv_detail(tv_id, language) for tv_id in tv_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Failed to fetch TV detail", tv_id=tv_ids[i])
            else:
                successful_results.append(result)
        logger.info(
            "bulk_tv_details_completed",
            len=len(successful_results),
            successful_results=len(tv_ids),
        )
        return successful_results

    async def get_collection_detail(
        self,
        collection_id: int,
        language: str,
    ) -> TMDBCollection:
        """
        Fetches detailed information for a specific collection from TMDB.
        """
        url = f"{self.BASE_URL}/collection/{collection_id}"
        params = {
            "language": language,
        }
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            
            action="get_collection_detail",
        )

        collection_detail = TMDBCollection.model_validate(data)
        return collection_detail
