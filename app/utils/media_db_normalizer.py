from calendar import c
from datetime import datetime, timezone
import re
from typing import List, Optional
from app.models.api.anilist_models import AnilistMediaDetailed
from app.models.api.omdb_models import OMDbData
from app.models.api.tmdb_models import TMDBTVDetail
from app.models.db.media_db_models import (
    MediaInsert,
    MediaScore,
    MediaTitle,
    MediaTag,
)
from app.enums.media_enums import MediaExternalSource, MediaType
from app.utils.omdb_normalizer import normalize_omdb_rating
from app.utils.tmdb_normalizer import TMDBNormalizer
class MediaDBNormalizer:
    @staticmethod
    def clean_html(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text) if text else text


    @staticmethod
    def build_search_tokens(title: str, synonyms: Optional[List[str]]) -> List[str]:
        tokens = set()

        def process(text: str):
            if not text:
                return

            text = text.lower()

            # remove special chars
            text = re.sub(r"[^\w\s]", "", text)

            # split into words
            words = text.split()

            # add full phrase + words
            tokens.add(text)
            tokens.update(words)

        process(title)

        if synonyms:
            for syn in synonyms:
                process(syn)

        return list(tokens)

    @staticmethod
    def normalize_anilist_to_media_core(anilist: AnilistMediaDetailed) -> MediaInsert:
        # Normalize title

        raw_title = (
            anilist.title.english or anilist.title.romaji or anilist.title.native or ""
        )
        raw_title = raw_title or f"media-{anilist.id}"
        normalized = re.sub(r"[^\w\s]", "", raw_title).lower()
        normalized = re.sub(r"\s+", " ", normalized).strip()
        title = MediaTitle(
            title=raw_title,
            normalized=normalized,
            romaji=anilist.title.romaji,
            native=anilist.title.native,
            english=anilist.title.english,
        )

        # Normalize tags
        tags: List[MediaTag] = (
            [
                MediaTag(
                    name=tag.name,
                    is_media_spoiler=tag.is_media_spoiler,
                    is_general_spoiler=tag.is_general_spoiler,
                )
                for tag in anilist.tags
            ]
            if anilist.tags
            else []
        )

        search_tokens = MediaDBNormalizer.build_search_tokens(title.normalized, anilist.synonyms)

        # Normalize genres
        genres = anilist.genres if anilist.genres else []

        # Normalize images
        cover_image = (
            anilist.cover_image.extra_large
            or anilist.cover_image.large
            or anilist.cover_image.medium
            if anilist.cover_image
            else None
        )
        banner_image = anilist.banner_image

        description = MediaDBNormalizer.clean_html(anilist.description) if anilist.description else None

        def parse_date(media_date):
            if not media_date or not media_date.year:
                return None
            try:
                return datetime(
                    year=media_date.year,
                    month=media_date.month or 1,
                    day=media_date.day or 1,
                )
            except Exception:
                return None

        release_date = parse_date(anilist.start_date)
        end_date = parse_date(anilist.end_date)

        slug = re.sub(r"[^\w\s-]", "", title.normalized)
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-_")
        base_slug = slug if slug else "media"
        slug = f"{base_slug}-{anilist.id}"

        scores = []
        if anilist.average_score is not None:
            scores.append(
                MediaScore(
                    value=float(anilist.average_score),
                    source=MediaExternalSource.ANILIST.value,
                )
            )

        # Compose MediaInsert
        return MediaInsert(
            external_id=anilist.id,
            external_source=MediaExternalSource.ANILIST,
            media_type=MediaType[anilist.type.upper()],
            title=title,
            search_tokens=search_tokens,
            description=description,
            is_adult=anilist.is_adult or False,
            status=anilist.status,
            format=anilist.format,
            season=anilist.season,
            season_year=anilist.season_year,
            release_date=release_date,
            end_date=end_date,
            cover_image=cover_image,
            banner_image=banner_image,
            genres=genres,
            tags=tags,
            synonyms=anilist.synonyms,
            slug=slug,
            popularity=anilist.popularity,
            scores=scores,
        )


    from app.models.api.tmdb_models import TMDBTVDetail, TMDBMovieDetail

    @staticmethod
    def build_tmdb_title(detail) -> MediaTitle:
        # Prefer English title, then original, then name
        raw_title = (
            getattr(detail, "title", None)
            or getattr(detail, "original_title", None)
            or getattr(detail, "name", None)
            or getattr(detail, "original_name", None)
            or ""
        )
        normalized = re.sub(r"[^\w\s]", "", raw_title).lower()
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return MediaTitle(
            title=raw_title,
            normalized=normalized,
            romaji=None,
            native=None,
            english=None,
        )

    @staticmethod
    def build_tmdb_search_tokens(title: str, alt_titles: Optional[List[str]]) -> List[str]:
        tokens = set()

        def process(text: str):
            if not text:
                return
            text = text.lower()
            text = re.sub(r"[^\w\s]", "", text)
            words = text.split()
            tokens.add(text)
            tokens.update(words)

        process(title)
        if alt_titles:
            for alt in alt_titles:
                process(alt)
        return list(tokens)

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
    ) -> MediaInsert:
        title = MediaDBNormalizer.build_tmdb_title(tv)
        alt_titles = TMDBNormalizer.get_tv_alternative_titles(tv.alternative_titles)
        search_tokens = MediaDBNormalizer.build_tmdb_search_tokens(title.normalized, alt_titles)
        genres = [g.name for g in tv.genres] if tv.genres else []
        cover_image = TMDBNormalizer.get_image_url(
            tv.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
        )

        banner_image = TMDBNormalizer.get_image_url(
            tv.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
        )

        slug = re.sub(r"[^\w\s-]", "", title.normalized)
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-_")
        base_slug = slug if slug else "media"
        slug = f"{base_slug}-{tv.id}"

        format = (
            tv.type
        )  # TMDB has no format field; type (e.g. "Scripted") is the closest equivalent
        
        keywords = TMDBNormalizer.get_tv_keywords(tv.keywords)

        scores = normalize_omdb_rating(omdb_data) if omdb_data else []
        
        if tv.vote_average is not None:
            scores.append(
                MediaScore(
                    value=float(tv.vote_average),
                    source=MediaExternalSource.TMDB.value,
                    vote_count=tv.vote_count,
                )
            )

        return MediaInsert(
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
    ) -> MediaInsert:
        title = MediaDBNormalizer.build_tmdb_title(movie)
        alt_titles = TMDBNormalizer.get_alternative_titles(movie.alternative_titles)
        search_tokens = MediaDBNormalizer.build_tmdb_search_tokens(title.normalized, alt_titles)
        genres = [g.name for g in movie.genres] if movie.genres else []
        cover_image = TMDBNormalizer.get_image_url(
            movie.poster_path, TMDBNormalizer.TMDB_POSTER_SIZE
        )
        banner_image = TMDBNormalizer.get_image_url(
            movie.backdrop_path, TMDBNormalizer.TMDB_BACKDROP_SIZE
        )
        slug = re.sub(r"[^\w\s-]", "", title.normalized)
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-_")
        base_slug = slug if slug else "media"
        slug = f"{base_slug}-{movie.id}"
        scores = normalize_omdb_rating(omdb_data) if omdb_data else []
        
        if movie.vote_average is not None:
            scores.append(
                MediaScore(
                    value=float(movie.vote_average),
                    source=MediaExternalSource.TMDB.value,
                    vote_count=movie.vote_count,
                )
            )
            
        keywords = TMDBNormalizer.get_movie_keywords(movie.keywords)

        return MediaInsert(
            external_id=movie.id,
            external_source=MediaExternalSource.TMDB,
            media_type=MediaType.MOVIE,
            title=title,
            search_tokens=search_tokens,
            description=movie.overview,
            is_adult=movie.adult,
            status=movie.status,
            format="movie", # TMDB has no format field for movies; we can just set it to "movie"
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
