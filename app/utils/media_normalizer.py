from typing import List
from app.models.anilist_models import AnilistMediaMinimal, AnilistMediaDetailed, AnilistPageInfo
from app.models.tmdb_models import TMDBMediaMinimal, TMDBTVDetail, TMDBMovieDetail
from app.models.media_models import MediaMinimal, MediaPagination, MediaDetailed
from app.utils.genre_utils import get_movie_genre_name_by_id, get_tv_genre_name_by_id


class MediaNormalizer:

    @staticmethod
    def normalize_anilist_minimal(
        results: List[AnilistMediaMinimal],
    ) -> List[MediaMinimal]:
        media_list = []

        for media in results:
            media_dict = media.model_dump()
            media_dict["media_source"] = "anilist"
            media_dict["media_type"] = "anime"
            media_dict["title"] = media.title.english or media.title.romaji or media.title.native
            media_dict["cover_image"] = media.cover_image.large
            media_dict["start_date"] = (
                f"{media.start_date.year}-{media.start_date.month:02d}-{media.start_date.day:02d}"
                if media.start_date
                and media.start_date.year
                and media.start_date.month
                and media.start_date.day
                else None
            )
            media_dict["end_date"] = (
                f"{media.end_date.year}-{media.end_date.month:02d}-{media.end_date.day:02d}"
                if media.end_date
                and media.end_date.year
                and media.end_date.month
                and media.end_date.day
                else None
            )
            media_list.append(MediaMinimal.model_validate(media_dict))
        return media_list

    @staticmethod
    def normalize_anilist_minimal_pagination(
        results: List[AnilistMediaMinimal],
        page_info: AnilistPageInfo,
    ) -> MediaPagination:

        media_list: List[MediaMinimal] = MediaNormalizer.normalize_anilist_minimal(results)

        return MediaPagination(
            results=media_list,
            current_page=page_info.current_page,  # type: ignore
            per_page=page_info.per_page,  # type: ignore
            has_next_page=page_info.has_next_page,  # type: ignore
            total=page_info.total,
        )

    @staticmethod
    def normalize_anilist_detailed(media: AnilistMediaDetailed) -> MediaDetailed:
        media_dict = media.model_dump()
        media_dict["media_source"] = "anilist"
        media_dict["media_type"] = "anime"
        media_dict["title"] = media.title.english or media.title.romaji or media.title.native
        media_dict["cover_image"] = media.cover_image.large
        media_dict["start_date"] = (
            f"{media.start_date.year}-{media.start_date.month:02d}-{media.start_date.day:02d}"
            if media.start_date
            and media.start_date.year
            and media.start_date.month
            and media.start_date.day
            else None
        )
        media_dict["end_date"] = (
            f"{media.end_date.year}-{media.end_date.month:02d}-{media.end_date.day:02d}"
            if media.end_date
            and media.end_date.year
            and media.end_date.month
            and media.end_date.day
            else None
        )
        media_dict["tags"] = [tag.name for tag in media.tags]
        media_dict["studios"] = [
            studio.name for studio in [edge.node for edge in media.studios.edges]
        ]
        return MediaDetailed.model_validate(media_dict)

    @staticmethod
    def normalize_tmdb_minimal(
        results: List[TMDBMediaMinimal], media_type: str
    ) -> List[MediaMinimal]:
        media_list = []

        for media in results:
            media_dict = media.model_dump()
            media_dict["media_source"] = "tmdb"
            media_dict["media_type"] = "movie" if media_type == "movie" else "tv"
            media_dict["title"] = (
                media.title or media.original_title or media.name or media.original_name
            )
            media_dict["genres"] = [
                (
                    get_movie_genre_name_by_id(genre_id)
                    if media_type == "movie"
                    else get_tv_genre_name_by_id(genre_id)
                )
                for genre_id in media.genre_ids
            ]
            media_dict["average_score"] = media.vote_average
            media_dict["format"] = None

            media_dict["cover_image"] = f"https://image.tmdb.org/t/p/original/{media.poster_path}"
            media_list.append(MediaMinimal.model_validate(media_dict))
        return media_list
