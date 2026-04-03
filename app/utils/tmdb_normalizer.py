from datetime import datetime
from typing import Callable, List, Optional

from app.enums.user_media_entry_enums import MediaExternalSource, MediaType
from app.models.media_models import (
    MediaBelongsToCollection,
    MediaCast,
    MediaMinimal,
    MediaRecommendation,
    MediaSeason,
    MovieCollection,
    MovieCollectionPart,
    MovieDetailed,
    TVDetailed,
)
from app.models.tmdb_models import (
    TMDBAlternativeTitles,
    TMDBAlternativeTitlesTv,
    TMDBBelongsToCollection,
    TMDBCollection,
    TMDBCredits,
    TMDBMediaMinimal,
    TMDBMediaMinimalRecommendation,
    TMDBMovieDetail,
    TMDBMovieKeywords,
    TMDBPaginationRecommendation,
    TMDBSeason,
    TMDBTVDetail,
    TMDBTvKeywords,
)
from app.utils.genre_utils import get_movie_genre_name_by_id, get_tv_genre_name_by_id
import structlog

logger = structlog.get_logger("tmdb_normalizer")


class TMDBNormalizer:
    """Normalizer for TMDB data."""

    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
    TMDB_POSTER_SIZE = "w500"
    TMDB_BACKDROP_SIZE = "w1280"
    TMDB_PROFILE_SIZE = "w185"
    TMDB_COLLECTION_BACKDROP_SIZE = "w1440_and_h320_multi_faces"

    MAX_CAST = 6
    MAX_RECOMMENDATIONS = 7

    @staticmethod
    def normalize_minimal(
        results: List[TMDBMediaMinimal], media_type: str
    ) -> List[MediaMinimal]:
        """Normalize TMDB minimal media list."""
        media_list: List[MediaMinimal] = []
        try:
            for media in results:
                normalized_media = MediaMinimal(
                    id=media.id,
                    mediaType=media_type.upper(),
                    externalSource=MediaExternalSource.TMDB,
                    title=TMDBNormalizer._get_title(media),
                    genres=TMDBNormalizer._get_genres(media.genre_ids, media_type),
                    averageScore=round(media.vote_average, 1),
                    format=media.media_type,
                    coverImage=TMDBNormalizer._get_image_url(
                        media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                    ),
                    releaseDate=media.release_date,
                    firstAirDate=media.first_air_date,
                )  # type: ignore
                media_list.append(normalized_media)
        except Exception as exc:
            logger.error("normalize_tmdb_minimal", error=str(exc))
        return media_list

    @staticmethod
    def normalize_movie_detailed(media: TMDBMovieDetail) -> MovieDetailed:
        """Normalize TMDB movie data to MovieDetailed."""
        try:
            title = media.title or media.original_title or ""
            cover_image = TMDBNormalizer._get_image_url(
                media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            )
            banner_image = TMDBNormalizer._get_image_url(
                media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
            )
            belongs_to_collection = TMDBNormalizer._get_belongs_to_collection(
                media.belongs_to_collection
            )
            alternative_titles = TMDBNormalizer._get_alternative_titles(
                media.alternative_titles
            )
            keywords = TMDBNormalizer._get_movie_keywords(media.keywords)
            credits = TMDBNormalizer._get_cast(media.credits)
            recommendations = TMDBNormalizer._get_movie_recommendations(
                media.recommendations
            )

            return MovieDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType=MediaType.MOVIE,
                title=title,
                format="movie",  # TMDB has no format field so "movie" is the closest equivalent
                genres=[genre.name for genre in media.genres],
                status=media.status,
                coverImage=cover_image,
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=banner_image,
                originCountry=media.origin_country,
                isAdult=media.adult,
                originalLanguage=media.original_language,
                releaseDate=media.release_date,
                budget=media.budget,
                revenue=media.revenue,
                runtime=media.runtime,
                belongsToCollection=belongs_to_collection,
                alternativeTitles=alternative_titles,
                keywords=keywords,
                credits=credits,
                productionCompanies=[
                    company.name for company in media.production_companies
                ],
                recommendations=recommendations,
                spokenLanguages=[
                    language.english_name for language in media.spoken_languages
                ],
                synonyms=alternative_titles,
            )
        except Exception as exc:
            logger.error(
                "normalize_tmdb_detailed_movie", error=str(exc), media_id=media.id
            )
            raise

    @staticmethod
    def normalize_tv_detailed(media: TMDBTVDetail) -> TVDetailed:
        """Normalize TMDB TV data to TVDetailed."""
        try:
            title = media.name or media.original_name or ""
            cover_image = TMDBNormalizer._get_image_url(
                media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            )
            banner_image = TMDBNormalizer._get_image_url(
                media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
            )
            seasons = TMDBNormalizer._get_seasons(media.seasons)
            keywords = TMDBNormalizer._get_tv_keywords(media.keywords)
            credits = TMDBNormalizer._get_cast(media.credits)
            recommendations = TMDBNormalizer._get_tv_recommendations(
                media.recommendations
            )
            alternative_titles = TMDBNormalizer._get_tv_alternative_titles(
                media.alternative_titles
            )
            
            return TVDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType=MediaType.TV,
                title=title,
                format=media.type,  # TMDB has no format field; type (e.g. "Scripted") is the closest equivalent
                genres=[genre.name for genre in media.genres],
                status=media.status,
                coverImage=cover_image,
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=banner_image,
                isAdult=media.adult,
                originalLanguage=media.original_language,
                firstAirDate=media.first_air_date,
                lastAirDate=media.last_air_date,
                createdBy=(
                    [creator.name for creator in media.created_by]
                    if media.created_by
                    else None
                ),
                numberOfEpisodes=media.number_of_episodes,
                numberOfSeasons=media.number_of_seasons,
                nextEpisodeToAir=media.next_episode_to_air,
                seasons=seasons,
                type=media.type,
                inProduction=media.in_production,
                languages=media.languages,
                lastEpisodeToAir=media.last_episode_to_air,
                networks=(
                    [network.name for network in media.networks]
                    if media.networks
                    else None
                ),
                keywords=keywords,
                credits=credits,
                recommendations=recommendations,
                productionCountries=(
                    [country.name for country in media.production_countries]
                    if media.production_countries
                    else None
                ),
                synonyms=alternative_titles,
            )
        except Exception as exc:
            logger.error(
                "normalize_tmdb_detailed_tv", error=str(exc), media_id=media.id
            )
            raise

    @staticmethod
    def _get_image_url(path: Optional[str], size: str) -> str:
        """Construct TMDB image URL."""
        if not path:
            return ""
        return f"{TMDBNormalizer.TMDB_IMAGE_BASE}/{size}{path}"

    @staticmethod
    def _get_title(media: TMDBMediaMinimal) -> str:
        return (
            media.title
            or media.original_title
            or media.name
            or media.original_name
            or ""
        )

    @staticmethod
    def _get_genres(genre_ids: List[int], media_type: str) -> List[str]:
        """Convert genre IDs to genre names."""
        if media_type == "movie":
            return [
                name
                for genre_id in genre_ids
                if (name := get_movie_genre_name_by_id(genre_id)) is not None
            ]

        return [
            name
            for genre_id in genre_ids
            if (name := get_tv_genre_name_by_id(genre_id)) is not None
        ]

    @staticmethod
    def _extract_alternative_titles(
        alternative_titles: Optional[TMDBAlternativeTitles | TMDBAlternativeTitlesTv],
        list_attr: str,
    ) -> Optional[List[str]]:
        if not alternative_titles:
            return None

        items = getattr(alternative_titles, list_attr, None)
        if not items:
            return None

        return [item.title for item in items]

    @staticmethod
    def _get_alternative_titles(
        alternative_titles: Optional[TMDBAlternativeTitles],
    ) -> Optional[List[str]]:
        return TMDBNormalizer._extract_alternative_titles(alternative_titles, "titles")

    @staticmethod
    def _get_tv_alternative_titles(
        alternative_titles: Optional[TMDBAlternativeTitlesTv],
    ) -> Optional[List[str]]:
        """Extract TV alternative titles."""
        return TMDBNormalizer._extract_alternative_titles(alternative_titles, "results")

    @staticmethod
    def _extract_keyword_names(
        keywords: Optional[TMDBMovieKeywords | TMDBTvKeywords],
        list_attr: str,
    ) -> Optional[List[str]]:
        if not keywords:
            return None

        items = getattr(keywords, list_attr, None)
        if not items:
            return None

        return [keyword.name for keyword in items]

    @staticmethod
    def _get_movie_keywords(
        keywords: Optional[TMDBMovieKeywords],
    ) -> Optional[List[str]]:
        """Extract movie keywords."""
        return TMDBNormalizer._extract_keyword_names(keywords, "keywords")

    @staticmethod
    def _get_tv_keywords(keywords: Optional[TMDBTvKeywords]) -> Optional[List[str]]:
        """Extract TV keywords."""
        return TMDBNormalizer._extract_keyword_names(keywords, "results")

    @staticmethod
    def _get_cast(
        credits: Optional[TMDBCredits], limit: int = MAX_CAST
    ) -> Optional[List[MediaCast]]:
        """Extract and normalize cast information."""
        if not credits:
            return None

        return [
            MediaCast(
                name=cast_member.name,
                character=cast_member.character,
                castImage=TMDBNormalizer._get_image_url(
                    cast_member.profile_path, TMDBNormalizer.TMDB_PROFILE_SIZE
                ),
            )
            for cast_member in credits.cast[:limit]
        ]

    @staticmethod
    def _extract_recommendations(
        recommendations: Optional[TMDBPaginationRecommendation],
        title_getter: Callable[[TMDBMediaMinimalRecommendation], str],
        limit: int,
    ) -> Optional[List[MediaRecommendation]]:
        if not recommendations:
            return None

        return [
            MediaRecommendation(
                id=recommendation.id,
                title=title_getter(recommendation),
                coverImage=TMDBNormalizer._get_image_url(
                    recommendation.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                mediaType=MediaType[recommendation.media_type.upper()],
            )
            for recommendation in recommendations.results[:limit]
        ]

    @staticmethod
    def _get_movie_recommendation_title(
        recommendation: TMDBMediaMinimalRecommendation,
    ) -> str:
        return recommendation.title or recommendation.original_title or ""

    @staticmethod
    def _get_tv_recommendation_title(
        recommendation: TMDBMediaMinimalRecommendation,
    ) -> str:
        return (
            recommendation.title
            or recommendation.name
            or recommendation.original_title
            or recommendation.original_name
            or ""
        )

    @staticmethod
    def _get_movie_recommendations(
        recommendations: Optional[TMDBPaginationRecommendation],
        limit: int = MAX_RECOMMENDATIONS,
    ) -> Optional[List[MediaRecommendation]]:
        """Extract movie recommendations."""
        return TMDBNormalizer._extract_recommendations(
            recommendations,
            TMDBNormalizer._get_movie_recommendation_title,
            limit,
        )

    @staticmethod
    def _get_tv_recommendations(
        recommendations: Optional[TMDBPaginationRecommendation],
        limit: int = MAX_RECOMMENDATIONS,
    ) -> Optional[List[MediaRecommendation]]:
        """Extract TV recommendations."""
        return TMDBNormalizer._extract_recommendations(
            recommendations,
            TMDBNormalizer._get_tv_recommendation_title,
            limit,
        )

    @staticmethod
    def _get_belongs_to_collection(
        collection: Optional[TMDBBelongsToCollection],
    ) -> Optional[MediaBelongsToCollection]:
        """Normalize belongs-to-collection payload."""
        if not collection:
            return None

        return MediaBelongsToCollection(
            id=collection.id,
            name=collection.name,
            posterPath=TMDBNormalizer._get_image_url(
                collection.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            ),
            backdropPath=TMDBNormalizer._get_image_url(
                collection.backdrop_path, TMDBNormalizer.TMDB_COLLECTION_BACKDROP_SIZE
            ),
        )

    @staticmethod
    def _get_seasons(
        seasons: Optional[List[TMDBSeason]],
    ) -> Optional[List[MediaSeason]]:
        """Normalize seasons."""
        if not seasons:
            return None
        
        return [
            MediaSeason(
                airDate=season.air_date,
                episodeCount=season.episode_count,
                name=season.name,
                overview=season.overview,
                posterPath=TMDBNormalizer._get_image_url(
                    season.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                seasonNumber=season.season_number,
            )
            for season in seasons
        ]

    @staticmethod
    def _get_movie_collection(collection: TMDBCollection) -> Optional[MovieCollection]:
        """Normalize TMDB collection data to MovieCollection."""
        if not collection:
            return None

        normalized_parts: List[MovieCollectionPart] = []
        for part in collection.parts:
            media_type_key = part.media_type.upper()
            if media_type_key not in MediaType.__members__:
                logger.warning(
                    "skip_collection_part_invalid_media_type",
                    part_id=part.id,
                    media_type=part.media_type,
                )
                continue

            normalized_parts.append(
                MovieCollectionPart(
                    backdropPath=TMDBNormalizer._get_image_url(
                        part.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
                    ),
                    id=part.id,
                    title=part.title,
                    mediaType=MediaType[media_type_key],
                    releaseDate=part.release_date,
                    posterPath=TMDBNormalizer._get_image_url(
                        part.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                    ),
                )
            )

        return MovieCollection(
            id=collection.id,
            name=collection.name,
            overview=collection.overview,
            posterPath=TMDBNormalizer._get_image_url(
                collection.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            ),
            backdropPath=TMDBNormalizer._get_image_url(
                collection.backdrop_path, TMDBNormalizer.TMDB_COLLECTION_BACKDROP_SIZE
            ),
            parts=normalized_parts,
        )

    