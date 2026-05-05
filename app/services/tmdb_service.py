from typing import Optional, List

from app.integrations.tmdb_api import TMDBApi

from app.models.api.media_response import (
    MediaPagination,
)
from app.utils.normalizers.tmdb_normalizer import TMDBNormalizer
from app.models.providers.tmdb_models import (
    TMDBMovieDetail,
    TMDBCollection,
    TMDBTVDetail,
)


class TMDBService:
    def __init__(self, tmdb_api: TMDBApi):
        self.tmdb_api = tmdb_api

    @staticmethod
    def _filter_recommendations(results):
        """
        Filters out anime (genre_id 16) with Japanese original language.
        """
        return [
            media
            for media in results
            if not (
                16 in getattr(media, "genre_ids", [])
                and getattr(media, "original_language", None) == "ja"
            )
        ]

    async def get_trending_media(
        self,
        media_type: str,
        time_window: str,
        language: str,
        page: int,
    ) -> MediaPagination:
        pagination = await self.tmdb_api.get_trending_media(
            media_type=media_type,
            time_window=time_window,
            language=language,
            page=page,
        )
        results = pagination.results
        per_page = len(results)

        filtered_results = [
            media
            for media in results
            if not (16 in media.genre_ids and media.original_language == "ja")
        ]
        results = TMDBNormalizer.normalize_minimal(filtered_results, media_type)

        return MediaPagination(
            results=results,
            currentPage=page,
            perPage=per_page,
            hasNextPage=per_page == 20,
        )

    async def search_movie(
        self,
        search: Optional[str],
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
    ) -> MediaPagination:
        if search:
            pagination = await self.tmdb_api.get_search_movie(
                query=search, page=page, language=language
            )
            results = pagination.results
            per_page = len(results)

            filtered_results = [
                media
                for media in results
                if not (16 in media.genre_ids and media.original_language == "ja")
            ]
            results = TMDBNormalizer.normalize_minimal(filtered_results, "movie")
        else:
            if without_keywords:
                keyword_list = without_keywords.split(",")
                if "281372" not in keyword_list:
                    keyword_list.append("281372")
                if "210024" not in keyword_list:
                    keyword_list.append("210024")
                without_keywords = ",".join(keyword_list)
            else:
                without_keywords = "281372,210024"

            pagination = await self.tmdb_api.get_discover_movie(
                page=page,
                language=language,
                sort_by=sort_by,
                primary_release_date_gte=primary_release_date_gte,
                primary_release_date_lte=primary_release_date_lte,
                with_genres=with_genres,
                with_keywords=with_keywords,
                with_runtime_gte=with_runtime_gte,
                with_runtime_lte=with_runtime_lte,
                with_original_language=with_original_language,
                without_genres=without_genres,
                without_keywords=without_keywords,
            )
            per_page = len(pagination.results)
            results = TMDBNormalizer.normalize_minimal(pagination.results, "movie")
        return MediaPagination(
            results=results,
            currentPage=page,
            perPage=20,
            hasNextPage=per_page == 20,
            total=pagination.total_results,
        )

    async def search_tv(
        self,
        search: Optional[str],
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
    ) -> MediaPagination:
        if search:
            pagination = await self.tmdb_api.get_search_tv(
                query=search, page=page, language=language
            )
            results = pagination.results
            per_page = len(results)
            filtered_results = [
                media
                for media in results
                if not (16 in media.genre_ids and media.original_language == "ja")
            ]
            results = TMDBNormalizer.normalize_minimal(filtered_results, "tv")
        else:
            if without_keywords:
                keyword_list = without_keywords.split(",")
                if "281372" not in keyword_list:
                    keyword_list.append("281372")
                if "210024" not in keyword_list:
                    keyword_list.append("210024")
                without_keywords = ",".join(keyword_list)
            else:
                without_keywords = "281372,210024"

            pagination = await self.tmdb_api.get_discover_tv(
                page=page,
                language=language,
                sort_by=sort_by,
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
                without_genres=without_genres,
                without_keywords=without_keywords,
            )
            per_page = len(pagination.results)
            results = TMDBNormalizer.normalize_minimal(pagination.results, "tv")
        return MediaPagination(
            results=results,
            currentPage=page,
            perPage=20,
            hasNextPage=per_page == 20,
            total=pagination.total_results,
        )

    async def get_movie_detail(
        self,
        movie_id: int,
        language: Optional[str] = "en-US",
    ) -> TMDBMovieDetail:
        res = await self.tmdb_api.get_movie_detail(movie_id=movie_id, language=language)
        if res.recommendations:
            filtered_results = self._filter_recommendations(res.recommendations.results)
            res.recommendations.results = filtered_results
        return res

    async def get_tv_detail(
        self,
        tv_id: int,
        language: Optional[str] = "en-US",
    ) -> TMDBTVDetail:
        res = await self.tmdb_api.get_tv_detail(tv_id=tv_id, language=language)
        if res.recommendations:
            filtered_results = self._filter_recommendations(res.recommendations.results)
            res.recommendations.results = filtered_results
        return res

    async def get_collection_detail(
        self,
        collection_id: int,
        language: Optional[str] = "en-US",
    ) -> Optional[TMDBCollection]:
        return await self.tmdb_api.get_collection_detail(
            collection_id=collection_id, language=language
        )

    async def search_keyword(
        self,
        query: str,
    ) -> List[dict]:
        """
        Searches for keywords on TMDB. Returns first 60 results (3 pages).
        """
        all_results = []

        for page in range(1, 4):  # pages 1, 2, 3
            results, page_info = await self.tmdb_api.search_keyword(
                query=query,
                page=page,
            )
            all_results.extend(results)

            if page >= page_info.total_pages:
                break

        return all_results[:60]
