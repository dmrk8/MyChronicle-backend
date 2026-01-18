from typing import List, Union
import datetime

import structlog
from app.models.anilist_models import (
    AnilistMediaMinimal,
    AnilistMediaDetailed,
    AnilistPageInfo,
)
from app.models.tmdb_models import TMDBMediaMinimal, TMDBTVDetail, TMDBMovieDetail
from app.models.media_models import (
    MediaBase,
    MediaMinimal,
    MediaPagination,
    MediaDetailed,
    AnimeDetailed,
    MangaDetailed,
    MediaDetailedUnion
)
from app.utils.genre_utils import get_movie_genre_name_by_id, get_tv_genre_name_by_id
from app.enums.user_media_entry_enums import MediaExternalSource, MediaType

logger = structlog.get_logger("media normalizer")


class MediaNormalizer:
    @staticmethod
    def _get_media_type(media_type_str: str) -> MediaType:
        """
        Helper function to get ReviewMediaType enum from a string (case-insensitive).
        """
        try:
            return MediaType(media_type_str.upper())
        except ValueError:
            raise ValueError(f"Invalid media type: {media_type_str}")

    @staticmethod
    def normalize_anilist_minimal(
        results: List[AnilistMediaMinimal],
    ) -> List[MediaMinimal]:
        media_list = []
        try:
            for media in results:
                mm = MediaMinimal(
                    id=media.id,
                    mediaType=MediaNormalizer._get_media_type(media.type),
                    externalSource=MediaExternalSource.ANILIST,
                    title=media.title.english
                    or media.title.romaji
                    or media.title.native,
                    format=media.format,
                    genres=media.genres,
                    status=media.status,
                    coverImage=media.cover_image.extra_large,
                    bannerImage=media.banner_image,
                    averageScore=(
                        round(media.average_score / 10, 1)
                        if media.average_score
                        else None
                    ),
                    episodes=media.episodes,
                    mainStudio=next(
                        (
                            studio.node.name
                            for studio in media.studios.edges
                            if studio.is_main
                        ),
                        None,
                    ),
                    chapters=media.chapters,
                )  # type: ignore
                media_list.append(mm)
        except Exception as e:
            logger.info("normalize_anilist_minimal", error=str(e))
        return media_list

    @staticmethod
    def normalize_anilist_detailed(media: AnilistMediaDetailed) -> MediaDetailedUnion:
        if media.type == MediaType.ANIME:
            return AnimeDetailed(
                id=media.id,
                externalSource=MediaExternalSource.ANILIST,
                mediaType=MediaType.ANIME,
                title=media.title.english
                or media.title.romaji
                or media.title.native
                or "",
                format=media.format,
                genres=media.genres,
                status=media.status,
                coverImage=media.cover_image.large if media.cover_image else None,
                averageScore=(
                    round(media.average_score / 10, 1) if media.average_score else None
                ),
                description=media.description,
                bannerImage=media.banner_image,
                isAdult=media.is_adult,
                synonyms=media.synonyms,
                countryOfOrigin=media.country_of_origin,
                season=media.season,
                seasonYear=media.season_year,
                source=media.source,
                episodes=media.episodes,
                duration=media.duration,
                startDate=media.start_date,
                endDate=media.end_date,
                studios=media.studios,
                tags=media.tags,
                relations=media.relations,
                recommendations=media.recommendations,
                characters=media.characters,
                nextAiringEpisode=media.next_airing_episode,
            )
        elif media.type == MediaType.MANGA:
            return MangaDetailed(
                id=media.id,
                externalSource=MediaExternalSource.ANILIST,
                mediaType=MediaType.MANGA,
                title=media.title.english
                or media.title.romaji
                or media.title.native
                or "",
                format=media.format,
                genres=media.genres,
                status=media.status,
                coverImage=media.cover_image.large if media.cover_image else None,
                averageScore=(
                    round(media.average_score / 10, 1) if media.average_score else None
                ),
                description=media.description,
                bannerImage=media.banner_image,
                isAdult=media.is_adult,
                synonyms=media.synonyms,
                countryOfOrigin=media.country_of_origin,
                source=media.source,
                chapters=media.chapters,
                volumes=media.volumes,
                startDate=media.start_date,
                endDate=media.end_date,
                tags=media.tags,
                relations=media.relations,
                recommendations=media.recommendations,
                characters=media.characters,
            )
        else:
            raise ValueError(f"Unsupported media type: {media.type}")


    @staticmethod
    def normalize_tmdb_minimal(
        results: List[TMDBMediaMinimal], media_type: str
    ) -> List[MediaMinimal]:
        media_list = []
        try:
            for media in results:
                mm = MediaMinimal(
                    id=media.id,
                    mediaType=MediaNormalizer._get_media_type(media_type),
                    externalSource=MediaExternalSource.TMDB,
                    title=media.title
                    or media.original_title
                    or media.name
                    or media.original_name,
                    genres=[
                        (
                            get_movie_genre_name_by_id(genre_id)
                            if media_type == "movie"
                            else get_tv_genre_name_by_id(genre_id)
                        )
                        for genre_id in media.genre_ids
                    ],
                    averageScore=round(media.vote_average, 1),
                    format=media.media_type,
                    coverImage=f"https://image.tmdb.org/t/p/original/{media.poster_path}",
                    releaseDate=media.release_date,
                    firstAirDate=media.first_air_date,
                )  # type: ignore
                media_list.append(mm)
        except Exception as e:
            logger.info("normalize_tmdb_minimal", error=str(e))
        return media_list

    @staticmethod
    def normalize_tmdb_detailed(
        media: Union[TMDBMovieDetail, TMDBTVDetail],
    ) -> MediaDetailed:
        media_type = "movie" if isinstance(media, TMDBMovieDetail) else "tv"

        try:
            return MediaDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType=MediaNormalizer._get_media_type(media_type),
                title=(
                    (media.title or media.original_title)
                    if media_type == "movie"
                    else (media.name or media.original_name)
                ),
                format=media_type,
                genres=[m.name for m in media.genres],
                status=media.status,
                coverImage=f"https://image.tmdb.org/t/p/original/{media.poster_path}",
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=f"https://image.tmdb.org/t/p/original/{media.backdrop_path}",
                numberOfEpisodes=(
                    None if media_type == "movie" else media.number_of_episodes
                ),
                numberOfSeasons=(
                    None if media_type == "movie" else media.number_of_seasons
                ),
                studios=[s.name for s in media.production_companies],
                countryOfOrigin=(
                    media.origin_country[0] if media.origin_country else None
                ),
                isAdult=media.adult,
                originalLanguage=media.original_language,
                releaseDate=media.release_date if media_type == "movie" else None,
                budget=media.budget if media_type == "movie" else None,
                revenue=media.revenue if media_type == "movie" else None,
                runtime=media.runtime if media_type == "movie" else None,
                firstAirDate=media.first_air_date if media_type == "tv" else None,
                episodeRunTime=(
                    media.episode_run_time[0]
                    if media_type == "tv" and media.episode_run_time
                    else None
                ),
                lastAirDate=media.last_air_date if media_type == "tv" else None,
                type=media.type if media_type == "tv" else None,
            )  # type: ignore
        except Exception as e:
            logger.info("normalize_tmdb_detailed", error=str(e))
