from datetime import datetime, timezone
from typing import Callable, List, Optional

from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.shared.media import MediaTitle
from app.models.api.media_response_models import (
    MediaBelongsToCollection,
    MediaCast,
    MediaMinimal,
    MediaNextAiringEpisode,
    MediaRecommendation,
    MediaSeason,
    MovieCollection,
    MovieCollectionPart,
    MovieDetailed,
    TMDBMediaBase,
    TMDBMediaLastEpisodeToAir,
    TVDetailed,
    Trailer,
)
from app.models.providers.tmdb_models import (
    TMDBAlternativeTitles,
    TMDBAlternativeTitlesTv,
    TMDBBelongsToCollection,
    TMDBCollection,
    TMDBCredits,
    TMDBMediaMinimal,
    TMDBMediaMinimalRecommendation,
    TMDBMovieDetail,
    TMDBMovieKeywords,
    TMDBNextEpisodeToAir,
    TMDBPaginationRecommendation,
    TMDBSeason,
    TMDBTVDetail,
    TMDBTvKeywords,
    TMDBVideos,
)
from app.utils.genre_utils import get_movie_genre_name_by_id, get_tv_genre_name_by_id

from app.utils.normalizers.text_utils import normalize_title_text


class TMDBNormalizer:
    """Normalizer for TMDB data."""

    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
    TMDB_POSTER_SIZE = "w500"
    TMDB_BACKDROP_SIZE = "w1280"
    TMDB_PROFILE_SIZE = "w185"
    TMDB_COLLECTION_BACKDROP_SIZE = "w1440_and_h320_multi_faces"

    MAX_CAST = 6
    MAX_RECOMMENDATIONS = 20

    @staticmethod
    def normalize_minimal(
        results: List[TMDBMediaMinimal], media_type: str
    ) -> List[MediaMinimal]:
        """Normalize TMDB minimal media list."""
        media_list: List[MediaMinimal] = []

        for media in results:
            normalized_media = MediaMinimal(
                id=media.id,
                mediaType=media_type.upper(),
                externalSource=MediaExternalSource.TMDB,
                title=TMDBNormalizer._get_title(media),
                genres=TMDBNormalizer._get_genres(media.genre_ids, media_type),
                averageScore=(
                    round(media.vote_average, 1) if media.vote_average else None
                ),
                format=media.media_type,
                coverImage=TMDBNormalizer.get_image_url(
                    media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                releaseDate=media.release_date,
                firstAirDate=media.first_air_date,
            )  # type: ignore
            media_list.append(normalized_media)

        return media_list

    @staticmethod
    def normalize_tmdb_base_detailed(
        media: TMDBMovieDetail | TMDBTVDetail,
    ) -> TMDBMediaBase:
        if isinstance(media, TMDBMovieDetail):
            title = TMDBNormalizer._convert_title(media.title, media.original_title)

            keywords = TMDBNormalizer.get_movie_keywords(media.keywords)

            recommendations = TMDBNormalizer._get_movie_recommendations(
                media.recommendations
            )
            alternative_titles = TMDBNormalizer.get_movie_alternative_titles(
                media.alternative_titles
            )

        elif isinstance(media, TMDBTVDetail):
            title = TMDBNormalizer._convert_title(media.name, media.original_name)

            keywords = TMDBNormalizer.get_tv_keywords(media.keywords)

            recommendations = TMDBNormalizer._get_tv_recommendations(
                media.recommendations
            )
            alternative_titles = TMDBNormalizer.get_tv_alternative_titles(
                media.alternative_titles
            )

        credits = TMDBNormalizer._get_cast(media.credits)

        cover_image = TMDBNormalizer.get_image_url(
            media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
        )
        banner_image = TMDBNormalizer.get_image_url(
            media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
        )

        return TMDBMediaBase(
            mediaType=(
                MediaType.MOVIE if isinstance(media, TMDBMovieDetail) else MediaType.TV
            ),
            title=title,
            description=media.overview,
            alternativeTitles=alternative_titles,
            format=media.type if isinstance(media, TMDBTVDetail) else "movie",
            genres=[genre.name for genre in media.genres] if media.genres else [],
            status=media.status,
            isAdult=media.adult,
            coverImage=cover_image,
            bannerImage=banner_image,
            trailer=TMDBNormalizer.convert_trailer(media.videos),
            originalLanguage=media.original_language,
            keywords=keywords,
            credits=credits,
            recommendations=recommendations,
            contentRating=None
        )

    @staticmethod
    def normalize_movie_detailed(media: TMDBMovieDetail) -> MovieDetailed:
        """Normalize TMDB movie data to MovieDetailed."""
        shared_base = TMDBNormalizer.normalize_tmdb_base_detailed(media)

        belongs_to_collection = TMDBNormalizer._get_belongs_to_collection(
            media.belongs_to_collection
        )
        return MovieDetailed(
            **shared_base.model_dump(),
            releaseDate=media.release_date,
            budget=media.budget,
            revenue=media.revenue,
            runtime=media.runtime,
            belongsToCollection=belongs_to_collection,
            productionCompanies=(
                [company.name for company in media.production_companies]
                if media.production_companies
                else []
            ),
            spokenLanguages=(
                [language.english_name for language in media.spoken_languages]
                if media.spoken_languages
                else []
            ),
        )

    @staticmethod
    def normalize_tv_detailed(media: TMDBTVDetail) -> TVDetailed:
        """Normalize TMDB TV data to TVDetailed."""

        shared_base = TMDBNormalizer.normalize_tmdb_base_detailed(media)

        seasons = TMDBNormalizer._get_seasons(media.seasons)

        return TVDetailed(
            **shared_base.model_dump(),
            firstAirDate=media.first_air_date,
            lastAirDate=media.last_air_date,
            createdBy=(
                [creator.name for creator in media.created_by]
                if media.created_by
                else None
            ),
            numberOfEpisodes=media.number_of_episodes,
            numberOfSeasons=media.number_of_seasons,
            nextAiringEpisode=TMDBNormalizer._build_next_airing_episode(
                media.next_episode_to_air
            ),
            seasons=seasons,
            type=media.type,
            inProduction=media.in_production,
            languages=media.languages,
            lastEpisodeToAir=(
                TMDBMediaLastEpisodeToAir.model_validate(
                    media.last_episode_to_air.model_dump()
                )
                if media.last_episode_to_air
                else None
            ),
            networks=(
                [network.name for network in media.networks] if media.networks else None
            ),
            productionCountries=(
                [country.name for country in media.production_countries]
                if media.production_countries
                else None
            ),
        )

    @staticmethod
    def get_image_url(path: Optional[str], size: str) -> str:
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
    def get_movie_alternative_titles(
        alternative_titles: Optional[TMDBAlternativeTitles],
    ) -> Optional[List[str]]:
        if not alternative_titles:
            return None
        return TMDBNormalizer._extract_alternative_titles(alternative_titles, "titles")

    @staticmethod
    def get_tv_alternative_titles(
        alternative_titles: Optional[TMDBAlternativeTitlesTv],
    ) -> Optional[List[str]]:
        """Extract TV alternative titles."""
        if not alternative_titles:
            return None
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
    def get_movie_keywords(
        keywords: Optional[TMDBMovieKeywords],
    ) -> Optional[List[str]]:
        """Extract movie keywords."""
        return TMDBNormalizer._extract_keyword_names(keywords, "keywords")

    @staticmethod
    def get_tv_keywords(keywords: Optional[TMDBTvKeywords]) -> Optional[List[str]]:
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
                castImage=TMDBNormalizer.get_image_url(
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
                coverImage=TMDBNormalizer.get_image_url(
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
            posterPath=TMDBNormalizer.get_image_url(
                collection.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            ),
            backdropPath=TMDBNormalizer.get_image_url(
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
                posterPath=TMDBNormalizer.get_image_url(
                    season.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                seasonNumber=season.season_number,
            )
            for season in seasons
        ]

    @staticmethod
    def get_movie_collection(
        collection: Optional[TMDBCollection],
    ) -> Optional[MovieCollection]:
        """Normalize TMDB collection data to MovieCollection."""
        if not collection or not collection.parts:
            return None

        normalized_parts: List[MovieCollectionPart] = []
        for part in collection.parts:
            media_type_key = part.media_type.upper()
            if media_type_key not in MediaType.__members__:
                continue

            normalized_parts.append(
                MovieCollectionPart(
                    backdropPath=TMDBNormalizer.get_image_url(
                        part.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
                    ),
                    id=part.id,
                    title=part.title,
                    originalTitle=part.original_title,
                    mediaType=MediaType[media_type_key],
                    releaseDate=part.release_date,
                    posterPath=TMDBNormalizer.get_image_url(
                        part.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                    ),
                )
            )

        return MovieCollection(
            id=collection.id,
            name=collection.name,
            overview=collection.overview,
            posterPath=TMDBNormalizer.get_image_url(
                collection.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            ),
            backdropPath=TMDBNormalizer.get_image_url(
                collection.backdrop_path, TMDBNormalizer.TMDB_COLLECTION_BACKDROP_SIZE
            ),
            parts=normalized_parts,
        )

    @staticmethod
    def convert_trailer(trailer: Optional[TMDBVideos]) -> Optional[List[Trailer]]:
        """Convert TMDB trailer data to Trailer."""
        if not trailer or not trailer.results:
            return None

        # Find the first YouTube trailer
        trailers = []
        for video in trailer.results:
            if (
                video.site
                and video.site.lower() == "youtube"
                and video.type
                and video.type.lower() == "trailer"
            ):
                trailers.append(
                    Trailer(
                        url=f"https://www.youtube.com/watch?v={video.key}",
                        thumbnail=f"https://i.ytimg.com/vi/{video.key}/hqdefault.jpg",
                    )
                )

        return trailers if trailers else None

    @staticmethod
    def _convert_title(
        title: Optional[str], original_title: Optional[str]
    ) -> MediaTitle:
        """Convert title to MediaTitle with normalized field."""
        if not title and not original_title:
            return MediaTitle(
                title="", normalized="", romaji=None, native=None, english=None
            )

        title = title or original_title or ""

        normalized = normalize_title_text(title)

        return MediaTitle(
            title=title,
            normalized=normalized,
            romaji=None,
            native=None,
            english=None,
        )

    @staticmethod
    def _build_next_airing_episode(
        next_episode: Optional[TMDBNextEpisodeToAir],
    ) -> Optional[MediaNextAiringEpisode]:
        """Convert TMDB next airing episode data to MediaNextAiringEpisode."""
        if not next_episode or not next_episode.air_date :
            return None

        air_date = datetime.strptime(next_episode.air_date, "%Y-%m-%d")
        airing_at_str = air_date.replace(tzinfo=timezone.utc).isoformat()
        return MediaNextAiringEpisode(
            episodeNumber=next_episode.episode_number,
            airingAt=airing_at_str,
            seasonNumber=next_episode.season_number,
        )  
