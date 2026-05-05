from datetime import datetime, timezone
from typing import List, Optional
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.omdb_models import OMDbData
from app.models.db.media_db_models import (
    MediaTitle,
    MediaTag,
    MediaDBUpsert,
)
from app.enums.media_enums import MediaExternalSource, MediaType
from app.utils.normalizers.score_builder import ScoreBuilder
from app.utils.normalizers.text_utils import (
    build_search_tokens,
    build_slug,
    normalize_title_text,
)
from app.utils.normalizers.tmdb_normalizer import TMDBNormalizer

from app.models.providers.tmdb_models import TMDBTVDetail, TMDBMovieDetail


class MediaDBNormalizer:

    @staticmethod
    def _parse_anilist_date(media_date):
        if (
            not media_date
            or not media_date.year
            or not media_date.month
            or not media_date.day
        ):
            return None
        try:
            return datetime(
                year=media_date.year,
                month=media_date.month,
                day=media_date.day,
            )
        except Exception:
            return None

    @staticmethod
    def normalize_anilist_to_media_core(media: AnilistMediaDetail) -> MediaDBUpsert:
        raw_title = (
            media.title.english or media.title.romaji or media.title.native or ""
            if media.title
            else ""
        )
        normalized = normalize_title_text(raw_title)

        title = MediaTitle(
            title=raw_title,
            normalized=normalized,
            romaji=media.title.romaji if media.title else None,
            native=media.title.native if media.title else None,
            english=media.title.english if media.title else None,
        )

        # Normalize tags
        tags: List[MediaTag] = (
            [
                MediaTag(
                    name=tag.name,
                    is_media_spoiler=tag.is_media_spoiler,
                    is_general_spoiler=tag.is_general_spoiler,
                )
                for tag in media.tags
            ]
            if media.tags
            else []
        )

        search_tokens = build_search_tokens(title.normalized, media.synonyms)

        genres = media.genres if media.genres else []

        cover_image = (
            media.cover_image.extra_large
            or media.cover_image.large
            or media.cover_image.medium
            if media.cover_image
            else None
        )
        banner_image = media.banner_image

        slug = build_slug(title.normalized, media.id)

        scores = ScoreBuilder.build_anilist_score(media)

        # Compose MediaDBUpsert
        return MediaDBUpsert(
            external_id=media.id,
            external_source=MediaExternalSource.ANILIST,
            media_type=MediaType[media.type.upper()],
            title=title,
            search_tokens=search_tokens,
            description=media.description,
            is_adult=media.is_adult or False,
            status=media.status,
            format=media.format,
            season=media.season,
            season_year=media.season_year,
            release_date=MediaDBNormalizer._parse_anilist_date(media.start_date),
            end_date=MediaDBNormalizer._parse_anilist_date(media.end_date),
            cover_image=cover_image,
            banner_image=banner_image,
            genres=genres,
            tags=tags,
            synonyms=media.synonyms,
            slug=slug,
            popularity=media.popularity,
            scores=scores,
        )

    @staticmethod
    def parse_tmdb_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            return None

    @staticmethod
    def normalize_tmdb_tv_to_media_core(
        tv: TMDBTVDetail, omdb_data: Optional[OMDbData]
    ) -> MediaDBUpsert:
        raw_title = tv.name or tv.original_name or ""
        normalized = normalize_title_text(raw_title)
        title = MediaTitle(
            title=raw_title,
            normalized=normalized,
            romaji=None,
            native=None,
            english=None,
        )

        alt_titles = TMDBNormalizer.get_tv_alternative_titles(tv.alternative_titles)
        search_tokens = build_search_tokens(title.normalized, alt_titles)
        genres = [g.name for g in tv.genres] if tv.genres else []
        cover_image = TMDBNormalizer.get_image_url(
            tv.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
        )

        banner_image = TMDBNormalizer.get_image_url(
            tv.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
        )

        slug = build_slug(title.normalized, tv.id)

        format = (
            tv.type
        )  # TMDB has no format field; type (e.g. "Scripted") is the closest equivalent

        keywords = TMDBNormalizer.get_tv_keywords(tv.keywords)

        scores = ScoreBuilder.build_tmdb_score(tv, omdb_data)

        return MediaDBUpsert(
            external_id=tv.id,
            external_source=MediaExternalSource.TMDB,
            media_type=MediaType.TV,
            title=title,
            search_tokens=search_tokens,
            description=tv.overview,
            is_adult=tv.adult,
            status=tv.status,
            format=format,
            season=None,
            season_year=None,
            release_date=MediaDBNormalizer.parse_tmdb_date(tv.first_air_date),
            end_date=MediaDBNormalizer.parse_tmdb_date(tv.last_air_date),
            cover_image=cover_image,
            banner_image=banner_image,
            genres=genres,
            tags=None,
            synonyms=alt_titles,
            slug=slug,
            popularity=tv.popularity,
            scores=scores,
            keywords=keywords,
        )

    @staticmethod
    def normalize_tmdb_movie_to_media_core(
        movie: TMDBMovieDetail, omdb_data: Optional[OMDbData] = None
    ) -> MediaDBUpsert:
        raw_title = movie.title or movie.original_title or ""
        normalized = normalize_title_text(raw_title)
        title = MediaTitle(
            title=raw_title,
            normalized=normalized,
            romaji=None,
            native=None,
            english=None,
        )
        alt_titles = TMDBNormalizer.get_movie_alternative_titles(
            movie.alternative_titles
        )

        search_tokens = build_search_tokens(title.normalized, alt_titles)

        genres = [g.name for g in movie.genres] if movie.genres else []
        cover_image = TMDBNormalizer.get_image_url(
            movie.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
        )
        banner_image = TMDBNormalizer.get_image_url(
            movie.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
        )

        slug = build_slug(title.normalized, movie.id)

        keywords = TMDBNormalizer.get_movie_keywords(movie.keywords)

        scores = ScoreBuilder.build_tmdb_score(movie, omdb_data)

        return MediaDBUpsert(
            external_id=movie.id,
            external_source=MediaExternalSource.TMDB,
            media_type=MediaType.MOVIE,
            title=title,
            search_tokens=search_tokens,
            description=movie.overview,
            is_adult=movie.adult,
            status=movie.status,
            format="movie",  # TMDB has no format field for movies; we can just set it to "movie"
            season=None,
            season_year=None,
            release_date=MediaDBNormalizer.parse_tmdb_date(movie.release_date),
            end_date=None,
            cover_image=cover_image,
            banner_image=banner_image,
            genres=genres,
            tags=None,
            synonyms=alt_titles,
            slug=slug,
            popularity=movie.popularity,
            scores=scores,
            keywords=keywords,
        )
