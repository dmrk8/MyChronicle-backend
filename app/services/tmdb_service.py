import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Union
from app.integrations.tmdb_api import TMDBApi
from app.models.tmdb_models import (
    TMDBPagination,
    TMDBMovieDetail,
    TMDBTVDetail,
    TMDBCollection,
    TMDBMediaMinimal,
    TMDBPageInfo,
)

from app.models.media_models import (
    MediaMinimal,
    MediaPagination,
    MediaFeaturedBulk,
    MovieCollection,
    MovieDetailed,
    TVDetailed,
)
from app.utils.tmdb_normalizer import TMDBNormalizer


class TMDBService:
    def __init__(self, tmdb_api: TMDBApi):
        self.tmdb_api = tmdb_api

    async def get_trending_media(
        self, media_type: str, time_window: str, language: str, page: int
    ) -> MediaPagination:
        results, page_info = await self.tmdb_api.get_trending_media(
            media_type=media_type, time_window=time_window, language=language, page=page
        )

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

    async def get_popular_season(
        self,
        media_type: str,
        start_date: str,
        end_date: str,
        page: int,
        language: str,
        sort_by: str,
    ) -> MediaPagination:
        results, page_info = await self.tmdb_api.get_popular_season(
            media_type=media_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            language=language,
            sort_by=sort_by,
        )
        per_page = len(results)
        results = TMDBNormalizer.normalize_minimal(results, media_type)

        return MediaPagination(
            results=results, currentPage=page, perPage=20, hasNextPage=per_page == 20
        )

    async def get_featured_bulk(
        self,
        media_type: str,
    ) -> MediaFeaturedBulk:
        media_type = media_type.lower()
        language = "en-US"
        popular_results, page_info = await self.tmdb_api.get_popular_season(
            media_type=media_type,
            start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            page=1,
            language=language,
            sort_by="popularity.desc",
        )
        popular_results = TMDBNormalizer.normalize_minimal(popular_results, media_type)

        trending_results, page_info = await self.tmdb_api.get_trending_media(
            media_type=media_type, time_window="week", language=language, page=1
        )

        filtered_trending_results = [
            media
            for media in trending_results
            if not (16 in media.genre_ids and media.original_language == "ja")
        ]
        trending_results = TMDBNormalizer.normalize_minimal(
            filtered_trending_results, media_type
        )

        return MediaFeaturedBulk(
            trending=trending_results, popularSeason=popular_results
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
            results, page_info = await self.tmdb_api.get_search_movie(
                query=search, page=page, language=language
            )
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

            results, page_info = await self.tmdb_api.get_discover_movie(
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
            per_page = len(results)
            results = TMDBNormalizer.normalize_minimal(results, "movie")
        return MediaPagination(
            results=results, currentPage=page, perPage=20, hasNextPage=per_page == 20
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
            results, page_info = await self.tmdb_api.get_search_tv(
                query=search, page=page, language=language
            )
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

            results, page_info = await self.tmdb_api.get_discover_tv(
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
            per_page = len(results)
            results = TMDBNormalizer.normalize_minimal(results, "tv")
        return MediaPagination(
            results=results, currentPage=page, perPage=20, hasNextPage=per_page == 20
        )

    async def get_movie_detail(
        self,
        movie_id: int,
        language: str,
    ) -> MovieDetailed:
        res = await self.tmdb_api.get_movie_detail(movie_id, language)
        if res.recommendations:
            filtered_results = [
                media
                for media in res.recommendations.results
                if not (16 in media.genre_ids and media.original_language == "ja")
            ]
            res.recommendations.results = filtered_results
        return TMDBNormalizer.normalize_movie_detailed(res)

    async def get_tv_detail(
        self,
        tv_id: int,
        language: str,
    ) -> TVDetailed:
        res = await self.tmdb_api.get_tv_detail(tv_id, language)
        if res.recommendations:
            filtered_results = [
                media
                for media in res.recommendations.results
                if not (16 in media.genre_ids and media.original_language == "ja")
            ]
            res.recommendations.results = filtered_results
        return TMDBNormalizer.normalize_tv_detailed(res)

    async def search_movie_test(
        self,
        page: int,
        sort_by: str,
        language: str,
        search: str,
        genres: List[int],
        keywords: List[int],
        length_lte: int,
        length_gte: int,
        release_date_gte: Optional[str] = None,
        release_date_lte: Optional[str] = None,
        with_original_language: Optional[str] = None,
    ) -> TMDBPagination:
        if search:
            results, page_info = await self.tmdb_api.get_search_movie(
                query=search, page=page, language=language
            )

            media_ids = [media.id for media in results]
            detailed_results = await self.get_bulk_movie_details(media_ids, language)
            filtered_results = detailed_results

            if genres:
                genre_set = set(genres)
                filtered_results = [
                    media
                    for media in filtered_results
                    if genre_set.issubset(set(genre.id for genre in media.genres))
                ]

            if keywords:
                keywords_set = set(keywords)
                excluded_keyword = 210024  # anime
                filtered_results = [
                    media
                    for media in filtered_results
                    if media.keywords
                    and keywords_set.issubset(
                        media_keywords := {
                            keyword.id for keyword in media.keywords.keywords
                        }
                    )
                    and excluded_keyword not in media_keywords
                ]

            if length_lte or length_gte:
                filtered_results = [
                    media
                    for media in filtered_results
                    if media.runtime is not None
                    and length_gte <= media.runtime <= length_lte
                ]

            if release_date_gte or release_date_lte:
                filtered_results = [
                    media
                    for media in filtered_results
                    if media.release_date is not None
                    and (
                        release_date_gte is None
                        or media.release_date >= release_date_gte
                    )
                    and (
                        release_date_lte is None
                        or media.release_date <= release_date_lte
                    )
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

            results = [
                TMDBMediaMinimal.model_validate(media.model_dump())
                for media in filtered_results
            ]
            return TMDBPagination(
                results=results,
                page=page,
                total_pages=page_info.total_pages,  # type: ignore
                total_results=len(filtered_results),  # Approximate # type: ignore
            )
        else:
            return TMDBPagination(results=[], page=page, total_pages=1, total_results=0)  # type: ignore

    async def get_bulk_movie_details(
        self,
        movie_ids: List[int],
        language: str,
    ) -> List[TMDBMovieDetail]:
        results = await self.tmdb_api.get_bulk_movie_details(movie_ids, language)
        imdb_tasks = []
        for result in results:
            if result.imdb_id is not None:
                imdb_tasks.append(self.imdb_service.get_imdb_rating(result.imdb_id))
            else:
                imdb_tasks.append(
                    asyncio.sleep(0)
                )  # Placeholder task that does nothing

        imdb_ratings = await asyncio.gather(*imdb_tasks, return_exceptions=True)

        for i, result in enumerate(results):
            rating = imdb_ratings[i]
            if not isinstance(rating, Exception) and rating is not None:
                result.imdb_rating_count = rating.rating_count  # type: ignore
                result.imdb_rating_value = rating.rating_value  # type: ignore

        return results

    async def get_bulk_tv_details(
        self,
        tv_ids: List[int],
        language: str,
    ) -> List[TMDBTVDetail]:
        results = await self.tmdb_api.get_bulk_tv_details(tv_ids, language)
        imdb_tasks = []
        for result in results:
            if result.imdb_id is not None:
                imdb_tasks.append(self.imdb_service.get_imdb_rating(result.imdb_id))
            else:
                imdb_tasks.append(None)  # Placeholder

        imdb_ratings = await asyncio.gather(*imdb_tasks, return_exceptions=True)

        for i, result in enumerate(results):
            rating = imdb_ratings[i]
            if not isinstance(rating, Exception) and rating is not None:
                result.imdb_rating_count = rating.rating_count  # type: ignore
                result.imdb_rating_value = rating.rating_value  # type: ignore

        return results

    async def get_collection_detail(
        self,
        collection_id: int,
        language: str,
    ) -> MovieCollection:
        res = await self.tmdb_api.get_collection_detail(collection_id, language)
        return TMDBNormalizer._get_movie_collection(res)
