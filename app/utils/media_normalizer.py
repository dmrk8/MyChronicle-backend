from typing import List, Union
import datetime

import structlog
from app.models.anilist_models import AnilistMediaMinimal, AnilistMediaDetailed, AnilistPageInfo
from app.models.tmdb_models import TMDBMediaMinimal, TMDBTVDetail, TMDBMovieDetail
from app.models.media_models import MediaMinimal, MediaPagination, MediaDetailed
from app.utils.genre_utils import get_movie_genre_name_by_id, get_tv_genre_name_by_id

logger = structlog.get_logger("media normalizer")


class MediaNormalizer:

    @staticmethod
    def normalize_anilist_minimal(
        results: List[AnilistMediaMinimal],
    ) -> List[MediaMinimal]:
        media_list = []
        try:
            for media in results:
                mm = MediaMinimal(
                    id=media.id,
                    mediaType=media.type,
                    mediaSource="anilist",
                    title=media.title.english or media.title.romaji or media.title.native,
                    format=media.format,
                    genres=media.genres,
                    status=media.status,
                    coverImage=media.cover_image.extra_large,
                    averageScore=media.average_score,
                    episodes=media.episodes,
                    mainStudio=next(
                        (studio.node.name for studio in media.studios.edges if studio.is_main),
                        None,
                    ),
                    chapters=media.chapters,
                )  # type: ignore
                media_list.append(mm)
        except Exception as e:
            logger.info("normalize_anilist_minimal", error=str(e))
        return media_list

    @staticmethod
    def normalize_anilist_detailed(media: AnilistMediaDetailed) -> MediaDetailed:
        def format_date(date):
            if date and date.year:
                dt = datetime.date(date.year, date.month or 1, date.day or 1)
                return f"{dt.day} {dt.strftime('%B %Y')}"
            return None

        try:
            next_airing_str = None
            if media.next_airing_episode and media.next_airing_episode.airing_at is not None:
                dt = datetime.datetime.fromtimestamp(float(media.next_airing_episode.airing_at))
                next_airing_str = f"Episode {media.next_airing_episode.episode} airs on {dt.day} {dt.strftime('%B %Y')}"

            return MediaDetailed(
                id=media.id,
                mediaSource="anilist",
                mediaType=media.type,
                title=media.title.english or media.title.romaji or media.title.native,
                format=media.format,
                genres=media.genres,
                status=media.status,
                coverImage=media.cover_image.large,
                averageScore=media.average_score,
                description=media.description,
                bannerImage=media.banner_image,
                episodes=media.episodes,
                studios=[edge.node.name for edge in media.studios.edges],
                duration=media.duration,
                season=media.season,
                seasonYear=media.season_year,
                startDate=format_date(media.start_date),
                endDate=format_date(media.end_date),
                nextAiringEpisode=next_airing_str,
                countryOfOrigin=media.country_of_origin,
                isAdult=media.is_adult,
                source=media.source,
                synonyms=media.synonyms,
                chapters=media.chapters,
                volumes=media.volumes,
            )  # type: ignore
        except Exception as e:
            logger.info("normalize_anilist_detail", error=str(e))

    @staticmethod
    def normalize_tmdb_minimal(
        results: List[TMDBMediaMinimal], media_type: str
    ) -> List[MediaMinimal]:
        media_list = []
        try:
            for media in results:
                mm = MediaMinimal(
                    id=media.id,
                    mediaType=media_type,
                    mediaSource="tmdb",
                    title=media.title or media.original_title or media.name or media.original_name,
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
    def normalize_tmdb_detailed(media: Union[TMDBMovieDetail, TMDBTVDetail]) -> MediaDetailed:
        media_type = "movie" if isinstance(media, TMDBMovieDetail) else "tv"

        try:
            return MediaDetailed(
                id=media.id,
                mediaSource="tmdb",
                mediaType=media_type,
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
                numberOfEpisodes=None if media_type == "movie" else media.number_of_episodes,
                numberOfSeasons=None if media_type == "movie" else media.number_of_seasons,
                studios=[s.name for s in media.production_companies],
                countryOfOrigin=media.origin_country[0] if media.origin_country else None,
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
