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
    MediaRecommendation,
    MediaRelations,
    MediaStudios,
    MediaCharacters,
    MovieDetailed,
    TVDetailed,
    MediaDetailedUnion,
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
        relations = (
            [
                MediaRelations(
                    relationType=edge.relation_type,
                    id=edge.node.id,
                    title=edge.node.title.english
                    or edge.node.title.romaji
                    or edge.node.title.native
                    or "",
                    format=edge.node.format,
                    status=edge.node.status,
                )
                for edge in media.relations.edges
            ]
            if media.relations
            else None
        )

        recommendations = [
            MediaRecommendation(
                id=edge.node.media_recommendation.id,
                title=edge.node.media_recommendation.title,
                coverImage=edge.node.media_recommendation.cover_image,
            )
            for edge in media.recommendations.edges
        ] if media.recommendations else None
        

        characters = (
            [
                MediaCharacters(
                    role=edge.role,
                    image=edge.node.image.large,
                    name=edge.node.name.full,
                )
                for edge in media.characters.edges
            ]
            if media.characters
            else None
        )

        if media.type == MediaType.ANIME:
            studios = (
                [
                    MediaStudios(isMain=studio.is_main, name=studio.node.name)
                    for studio in media.studios.edges
                ]
                if media.studios
                else None
            )
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
                studios=studios,
                tags=media.tags,
                relations=relations,
                recommendations=recommendations,
                characters=characters,
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
                relations=relations,
                recommendations=recommendations,
                characters=characters,
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
    def normalize_tmdb_detailed_movie(media: TMDBMovieDetail) -> MediaDetailedUnion:
        try:
            return MovieDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType=MediaNormalizer._get_media_type("movie"),
                title=media.title or media.original_title or "",
                format="movie",
                genres=[m.name for m in media.genres],
                status=media.status,
                coverImage=f"https://image.tmdb.org/t/p/original/{media.poster_path}",
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=f"https://image.tmdb.org/t/p/original/{media.backdrop_path}",
                originCountry=media.origin_country,
                isAdult=media.adult,
                originalLanguage=media.original_language,
                releaseDate=media.release_date,
                budget=media.budget,
                revenue=media.revenue,
                runtime=media.runtime,
                belongsToCollection=media.belongs_to_collection,
                alternativeTitles=media.alternative_titles,
                keywords=media.keywords,
                credits=media.credits,
                productionCompanies=media.production_companies,
                recommendations=media.recommendations,
                spokenLanguages=media.spoken_languages,
                synonyms=[t.title for t in media.alternative_titles.titles],
            )
        except Exception as e:
            logger.error("normalize_tmdb_detailed_movie", error=str(e))
            raise

    @staticmethod
    def normalize_tmdb_detailed_tv(media: TMDBTVDetail) -> MediaDetailedUnion:
        try:
            return TVDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType=MediaNormalizer._get_media_type("movie"),
                title=media.name or media.original_name or "",
                format=media.type,
                genres=[m.name for m in media.genres],
                status=media.status,
                coverImage=f"https://image.tmdb.org/t/p/original/{media.poster_path}",
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=f"https://image.tmdb.org/t/p/original/{media.backdrop_path}",
                isAdult=media.adult,
                originalLanguage=media.original_language,
                firstAirDate=media.first_air_date,
                lastAirDate=media.last_air_date,
                createdBy=media.created_by,
                numberOfEpisodes=media.number_of_episodes,
                numberOfSeasons=media.number_of_seasons,
                nextEpisodeToAir=media.next_episode_to_air,
                seasons=media.seasons,
                type=media.type,
                inProduction=media.in_production,
                languages=media.languages,
                lastEpisodeToAir=media.last_episode_to_air,
                networks=media.networks,
                keywords=media.keywords,
                credits=media.credits,
                recommendations=media.recommendations,
                productionCountries=media.production_countries,
                synonyms=(
                    [t.title for t in media.alternative_titles.results]
                    if media.alternative_titles
                    else []
                ),
            )
        except Exception as e:
            logger.error("normalize_tmdb_detailed_movie", error=str(e))
            raise
