
from datetime import datetime, timezone
from typing import List, Optional

from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.shared.media import MediaTag, MediaTitle
from app.models.api.media_response_models import (
    LastEpisodeToAir,
    MediaBelongsToCollection,
    MediaCastMember,
    MediaMinimal,
    MediaRecommendation,
    MovieCollection,
    MovieCollectionPart,
    MovieData,
    MovieTVMediaBase,
    TVData,
    TVSeason,
    Trailer,
    UpcomingEpisode,
)
from app.models.providers.tmdb_models import (
    TMDBAlternativeTitles,
    TMDBAlternativeTitlesTv,
    TMDBBelongsToCollection,
    TMDBCollection,
    TMDBCredits,
    TMDBMediaMinimal,
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
                external_id=media.id,
                media_type=MediaType(media_type),
                external_source=MediaExternalSource.TMDB,
                title=TMDBNormalizer._get_title(media),
                genres=TMDBNormalizer._get_genres(media.genre_ids, media_type),
                average_score=(
                    round(media.vote_average, 1) if media.vote_average else None
                ),
                format=media.media_type,
                cover_image=TMDBNormalizer.get_image_url(
                    media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                release_date=media.release_date,
                first_air_date=media.first_air_date,
            )
            media_list.append(normalized_media)

        return media_list

    @staticmethod
    def normalize_tmdb_base_detailed(
        media: TMDBMovieDetail | TMDBTVDetail,
    ) -> MovieTVMediaBase:
        if isinstance(media, TMDBMovieDetail):
            title = TMDBNormalizer._convert_title(media.title, media.original_title)

            keywords = TMDBNormalizer._get_keywords(movie_keywords=media.keywords)

            recommendations = TMDBNormalizer._get_recommendations(media.recommendations)
            alternative_titles = TMDBNormalizer.get_alternative_titles(
                movie_alternative_titles=media.alternative_titles
            )

        elif isinstance(media, TMDBTVDetail):
            title = TMDBNormalizer._convert_title(media.name, media.original_name)

            keywords = TMDBNormalizer._get_keywords(tv_keywords=media.keywords)

            recommendations = TMDBNormalizer._get_recommendations(
                media.recommendations, is_tv=True
            )
            alternative_titles = TMDBNormalizer.get_alternative_titles(
                tv_alternative_titles=media.alternative_titles
            )

        credits = TMDBNormalizer._get_cast(media.credits)

        cover_image = TMDBNormalizer.get_image_url(
            media.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
        )
        banner_image = TMDBNormalizer.get_image_url(
            media.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
        )

        return MovieTVMediaBase(
            title=title,
            description=media.overview,
            synonyms=alternative_titles,
            format=media.type if isinstance(media, TMDBTVDetail) else "movie",
            genres=[genre.name for genre in media.genres] if media.genres else [],
            status=media.status,
            is_adult=media.adult,
            cover_image=cover_image,
            banner_image=banner_image,
            trailer=TMDBNormalizer.convert_trailer(media.videos),
            original_language=media.original_language,
            tags=keywords,
            cast=credits,
            recommendations=recommendations,
            content_rating=None,
        )

    @staticmethod
    def normalize_movie_detail(media: TMDBMovieDetail) -> MovieData:
        """Normalize TMDB movie data to MovieDetailed."""
        shared_base = TMDBNormalizer.normalize_tmdb_base_detailed(media)

        belongs_to_collection = TMDBNormalizer._get_belongs_to_collection(
            media.belongs_to_collection
        )
        return MovieData(
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
    def normalize_tv_detail(media: TMDBTVDetail) -> TVData:
        """Normalize TMDB TV data to TVDetailed."""

        shared_base = TMDBNormalizer.normalize_tmdb_base_detailed(media)

        seasons = TMDBNormalizer._get_seasons(media.seasons)

        return TVData(
            **shared_base.model_dump(),
            first_air_date=media.first_air_date,
            last_air_date=media.last_air_date,
            created_by=(
                [creator.name for creator in media.created_by]
                if media.created_by
                else []
            ),
            number_of_episodes=media.number_of_episodes,
            number_of_seasons=media.number_of_seasons,
            next_airing_episode=TMDBNormalizer._build_next_airing_episode(
                media.next_episode_to_air
            ),
            seasons=seasons if seasons else [],
            type=media.type,
            in_production=media.in_production,
            languages=media.languages if media.languages else [],
            last_episode_to_air=(
                LastEpisodeToAir.model_validate(media.last_episode_to_air.model_dump())
                if media.last_episode_to_air
                else None
            ),
            networks=(
                [network.name for network in media.networks] if media.networks else []
            ),
            production_countries=(
                [country.name for country in media.production_countries]
                if media.production_countries
                else []
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
    def get_alternative_titles(
        movie_alternative_titles: Optional[TMDBAlternativeTitles] = None,
        tv_alternative_titles: Optional[TMDBAlternativeTitlesTv] = None,
    ) -> List[str]:
        if movie_alternative_titles:
            items = movie_alternative_titles.titles
        elif tv_alternative_titles:
            items = tv_alternative_titles.results
        else:
            return []

        if not items:
            return []

        return [item.title for item in items]

    @staticmethod
    def _get_keywords(
        movie_keywords: Optional[TMDBMovieKeywords] = None,
        tv_keywords: Optional[TMDBTvKeywords] = None,
    ) -> List[MediaTag]:
        if movie_keywords:
            keywords = movie_keywords.keywords
        elif tv_keywords:
            keywords = tv_keywords.results
        else:
            return []

        return [MediaTag(name=keyword.name) for keyword in keywords]

    @staticmethod
    def _get_cast(
        credits: Optional[TMDBCredits], limit: int = MAX_CAST
    ) -> List[MediaCastMember]:
        """Extract and normalize cast information."""
        if not credits:
            return []

        return [
            MediaCastMember(
                name=cast_member.name,
                character=cast_member.character,
                image=TMDBNormalizer.get_image_url(
                    cast_member.profile_path, TMDBNormalizer.TMDB_PROFILE_SIZE
                ),
            )
            for cast_member in credits.cast[:limit]
        ]

    @staticmethod
    def _get_recommendations(
        recommendations: Optional[TMDBPaginationRecommendation],
        is_tv: bool = False,
        limit: int = MAX_RECOMMENDATIONS,
    ) -> List[MediaRecommendation]:
        """Extract and normalize recommendations."""
        if not recommendations:
            return []

        result = []
        for recommendation in recommendations.results[:limit]:
            title = (
                recommendation.title
                or recommendation.name
                or recommendation.original_title
                or recommendation.original_name
                or ""
                if is_tv
                else recommendation.title or recommendation.original_title or ""
            )

            result.append(
                MediaRecommendation(
                    id=recommendation.id,
                    title=title,
                    cover_image=TMDBNormalizer.get_image_url(
                        recommendation.poster_path,
                        TMDBNormalizer.TMDB_POSTER_SIZE,
                    ),
                    media_type=MediaType[recommendation.media_type.upper()],
                )
            )

        return result

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
            poster_image=TMDBNormalizer.get_image_url(
                collection.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            ),
            banner_image=TMDBNormalizer.get_image_url(
                collection.backdrop_path, TMDBNormalizer.TMDB_COLLECTION_BACKDROP_SIZE
            ),
        )

    @staticmethod
    def _get_seasons(
        seasons: Optional[List[TMDBSeason]],
    ) -> Optional[List[TVSeason]]:
        """Normalize seasons."""
        if not seasons:
            return None

        return [
            TVSeason(
                air_date=season.air_date,
                episode_count=season.episode_count,
                name=season.name,
                overview=season.overview,
                poster_image=TMDBNormalizer.get_image_url(
                    season.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                ),
                season_number=season.season_number,
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
                    banner_image=TMDBNormalizer.get_image_url(
                        part.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
                    ),
                    id=part.id,
                    title=part.title,
                    original_title=part.original_title,
                    media_type=MediaType[media_type_key],
                    release_date=part.release_date,
                    poster_image=TMDBNormalizer.get_image_url(
                        part.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
                    ),
                )
            )

        return MovieCollection(
            id=collection.id,
            name=collection.name,
            overview=collection.overview,
            poster_image=TMDBNormalizer.get_image_url(
                collection.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
            ),
            banner_image=TMDBNormalizer.get_image_url(
                collection.backdrop_path, TMDBNormalizer.TMDB_COLLECTION_BACKDROP_SIZE
            ),
            parts=normalized_parts,
        )

    @staticmethod
    def convert_trailer(trailer: Optional[TMDBVideos]) -> List[Trailer]:
        """Convert TMDB trailer data to Trailer."""
        if not trailer or not trailer.results:
            return []

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

        return trailers

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
    ) -> Optional[UpcomingEpisode]:
        """Convert TMDB next airing episode data to MediaNextAiringEpisode."""
        if not next_episode or not next_episode.air_date:
            return None

        air_date = datetime.strptime(next_episode.air_date, "%Y-%m-%d")
        airing_at_str = air_date.replace(tzinfo=timezone.utc).isoformat()
        return UpcomingEpisode(
            episode_number=next_episode.episode_number,
            airing_at=airing_at_str,
            season_number=next_episode.season_number,
        )
