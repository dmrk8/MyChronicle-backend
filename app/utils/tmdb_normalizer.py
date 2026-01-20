from typing import List, Optional
from app.enums.user_media_entry_enums import MediaExternalSource, MediaType
from app.models.media_models import (
    MediaCast,
    MediaMinimal,
    MediaRecommendation,
    MovieDetailed,
    TVDetailed,
    MediaBelongsToCollection,
    MediaSeason,
    MovieCollectionPart,
    MovieCollection,
)
from app.models.tmdb_models import (
    TMDBMediaMinimal,
    TMDBMovieDetail,
    TMDBTVDetail,
    TMDBPaginationRecommendation,
    TMDBCollection,
)
from app.utils.genre_utils import get_movie_genre_name_by_id, get_tv_genre_name_by_id
import structlog

logger = structlog.get_logger("tmdb_normalizer")


class TMDBNormalizer:
    """Normalizer for TMDB data"""

    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
    TMDB_POSTER_SIZE = "w500"
    TMDB_BACKDROP_SIZE = "w1280"  # ~1280x720, perfect for banners
    TMDB_PROFILE_SIZE = "w185"
    TMDB_COLLECTION_BACKDROP_SIZE = (
        "w1440_and_h320_multi_faces"  # For collection banners
    )

    @staticmethod
    def normalize_minimal(
        results: List[TMDBMediaMinimal], media_type: str
    ) -> List[MediaMinimal]:
        """Normalize TMDB minimal media list"""
        media_list = []
        try:
            for media in results:
                mm = MediaMinimal(
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
                )
                media_list.append(mm)
        except Exception as e:
            logger.error("normalize_tmdb_minimal", error=str(e))
        return media_list

    @staticmethod
    def normalize_movie_detailed(media: TMDBMovieDetail) -> MovieDetailed:
        """Normalize TMDB movie data to MovieDetailed"""
        try:
            return MovieDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType="MOVIE",
                title=media.title or media.original_title or "",
                format="movie",
                genres=[m.name for m in media.genres],
                status=media.status,
                coverImage=TMDBNormalizer._get_image_url(
                    media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=TMDBNormalizer._get_image_url(
                    media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
                ),
                originCountry=media.origin_country,
                isAdult=media.adult,
                originalLanguage=media.original_language,
                releaseDate=media.release_date,
                budget=media.budget,
                revenue=media.revenue,
                runtime=media.runtime,
                belongsToCollection=TMDBNormalizer._get_belongs_to_collection(
                    media.belongs_to_collection
                ),  # Updated to use helper method
                alternativeTitles=TMDBNormalizer._get_alternative_titles(
                    media.alternative_titles
                ),
                keywords=TMDBNormalizer._get_movie_keywords(media.keywords),
                credits=TMDBNormalizer._get_cast(media.credits),
                productionCompanies=[p.name for p in media.production_companies],
                recommendations=TMDBNormalizer._get_movie_recommendations(
                    media.recommendations
                ),
                spokenLanguages=[l.english_name for l in media.spoken_languages],
                synonyms=TMDBNormalizer._get_alternative_titles(
                    media.alternative_titles
                ),
            )
        except Exception as e:
            logger.error("normalize_tmdb_detailed_movie", error=str(e))
            raise

    @staticmethod
    def normalize_tv_detailed(media: TMDBTVDetail) -> TVDetailed:
        """Normalize TMDB TV data to TVDetailed"""
        try:
            return TVDetailed(
                id=media.id,
                externalSource=MediaExternalSource.TMDB,
                mediaType="TV",
                title=media.name or media.original_name or "",
                format=media.type,
                genres=[m.name for m in media.genres],
                status=media.status,
                coverImage=TMDBNormalizer._get_image_url(
                    media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                averageScore=round(media.vote_average, 1),
                description=media.overview,
                bannerImage=TMDBNormalizer._get_image_url(
                    media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
                ),
                isAdult=media.adult,
                originalLanguage=media.original_language,
                firstAirDate=media.first_air_date,
                lastAirDate=media.last_air_date,
                createdBy=[c.name for c in media.created_by],
                numberOfEpisodes=media.number_of_episodes,
                numberOfSeasons=media.number_of_seasons,
                nextEpisodeToAir=media.next_episode_to_air,
                seasons=TMDBNormalizer._get_seasons(media.seasons),
                type=media.type,
                inProduction=media.in_production,
                languages=media.languages,
                lastEpisodeToAir=media.last_episode_to_air,
                networks=[n.name for n in media.networks],
                keywords=TMDBNormalizer._get_tv_keywords(media.keywords),
                credits=TMDBNormalizer._get_cast(media.credits),
                recommendations=TMDBNormalizer._get_tv_recommendations(
                    media.recommendations
                ),
                productionCountries=[p.name for p in media.production_countries],
                synonyms=TMDBNormalizer._get_tv_alternative_titles(
                    media.alternative_titles
                ),
            )
        except Exception as e:
            logger.error("normalize_tmdb_detailed_tv", error=str(e))
            raise

    @staticmethod
    def _get_image_url(path: Optional[str], size: str) -> str:
        """Construct TMDB image URL"""
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
        """Convert genre IDs to genre names"""
        if media_type == "movie":
            return [
                name
                for gid in genre_ids
                if (name := get_movie_genre_name_by_id(gid)) is not None
            ]
        else:
            return [
                name
                for gid in genre_ids
                if (name := get_tv_genre_name_by_id(gid)) is not None
            ]

    @staticmethod
    def _get_alternative_titles(alternative_titles) -> Optional[List[str]]:
        if not alternative_titles:
            return None
        return [t.title for t in alternative_titles.titles]

    @staticmethod
    def _get_tv_alternative_titles(alternative_titles) -> Optional[List[str]]:
        """Extract TV alternative titles"""
        if not alternative_titles:
            return None
        return [t.title for t in alternative_titles.results]

    @staticmethod
    def _get_movie_keywords(keywords) -> Optional[List[str]]:
        """Extract movie keywords"""
        if not keywords:
            return None
        return [k.name for k in keywords.keywords]

    @staticmethod
    def _get_tv_keywords(keywords) -> Optional[List[str]]:
        """Extract TV keywords"""
        if not keywords:
            return None
        return [k.name for k in keywords.results]

    @staticmethod
    def _get_cast(credits, limit: int = 6) -> Optional[List[MediaCast]]:
        """Extract and normalize cast information"""
        if not credits:
            return None

        return [
            MediaCast(
                name=c.name,
                character=c.character,
                castImage=TMDBNormalizer._get_image_url(
                    c.profile_path, TMDBNormalizer.TMDB_PROFILE_SIZE
                ),
            )
            for c in credits.cast[:limit]
        ]

    @staticmethod
    def _get_movie_recommendations(
        recommendations: TMDBPaginationRecommendation, limit: int = 7
    ) -> Optional[List[MediaRecommendation]]:
        """Extract movie recommendations"""
        if not recommendations:
            return None

        return [
            MediaRecommendation(
                id=r.id,
                title=r.title or r.original_title or "",
                coverImage=TMDBNormalizer._get_image_url(
                    r.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                mediaType=MediaType[r.media_type.upper()],
            )
            for r in recommendations.results[:limit]
        ]

    @staticmethod
    def _get_tv_recommendations(
        recommendations: TMDBPaginationRecommendation, limit: int = 7
    ) -> Optional[List[MediaRecommendation]]:
        """Extract TV recommendations"""
        if not recommendations:
            return None

        return [
            MediaRecommendation(
                id=r.id,
                title=r.title or r.name or r.original_title or r.original_name or "",
                coverImage=TMDBNormalizer._get_image_url(
                    r.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                mediaType=MediaType[r.media_type.upper()],
            )
            for r in recommendations.results[:limit]
        ]

    @staticmethod
    def _get_belongs_to_collection(collection) -> Optional[MediaBelongsToCollection]:
        """Normalize belongs to collection"""
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
    def _get_seasons(seasons) -> Optional[List[MediaSeason]]:
        """Normalize seasons"""
        if not seasons:
            return None
        return [
            MediaSeason(
                airDate=s.air_date,
                episodeCount=s.episode_count,
                name=s.name,
                overview=s.overview,
                posterPath=TMDBNormalizer._get_image_url(
                    s.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                seasonNumber=s.season_number,
            )
            for s in seasons
        ]

    @staticmethod
    def _get_movie_collection(collection: TMDBCollection) -> Optional[MovieCollection]:
        """Normalize TMDB collection data to MovieCollection"""
        if not collection:
            return None

        normalized_parts = []
        for part in collection.parts:
            try:
                normalized_part = MovieCollectionPart(
                    backdropPath=TMDBNormalizer._get_image_url(
                        part.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
                    ),
                    id=part.id,
                    title=part.title,
                    mediaType=MediaType[part.media_type.upper()],
                    releaseDate=part.release_date,
                    posterPath=TMDBNormalizer._get_image_url(  # Add posterPath
                        part.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                    ),
                )
                normalized_parts.append(normalized_part)
            except KeyError:
                logger.warning(
                    f"Skipping collection part {part.id} due to invalid media_type: {part.media_type}"
                )
                continue

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
