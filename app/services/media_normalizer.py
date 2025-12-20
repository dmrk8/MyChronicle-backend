from typing import List
from app.models.anilist_models import AnilistMediaMinimal, AnilistMediaDetailed, AnilistPageInfo
from app.models.tmdb_models import TMDBMediaMinimal
from app.models.media_models import MediaMinimal, MediaPagination, MediaDetailed


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

        try:
            return MediaDetailed.model_validate(media_dict)
        except Exception as e:
            print(f"Error normalizing Anilist detailed media {media.id}: {str(e)}")
            raise  # Re-raise the exception or handle as needed
