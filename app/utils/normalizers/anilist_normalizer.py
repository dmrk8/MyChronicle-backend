from datetime import datetime, timezone
from typing import List, Optional
import calendar

from app.enums.media_enums import MediaExternalSource, MediaType, MediaStatus
from app.models.providers.anilist_models import (
    AnilistMediaDetail,
    AnilistMediaMinimal,
    AnilistTrailer,
    MediaDate,
    NextAiringEpisode,
    Relations,
    Recommendations,
    Characters,
    Studios,
    Title,
)
from app.models.shared.media import MediaTitle
from app.models.api.media_response_models import (
    AniMediaData,
    AnimeData,
    MangaData,
    MediaCharacter,
    MediaMinimal,
    MediaRecommendation,
    MediaRelation,
    MediaStudio,
    MediaVoiceActor,
    Trailer,
    UpcomingEpisode,
)
from app.models.shared.media import MediaTag
from app.utils.normalizers.text_utils import normalize_title_text, strip_html


class AnilistNormalizer:

    @staticmethod
    def normalize_minimal(results: List[AnilistMediaMinimal]) -> List[MediaMinimal]:
        """Normalize AniList minimal media list"""
        media_list = []
        for media in results:
            mm = MediaMinimal(
                external_id=media.id,
                media_type=MediaType(media.type.lower()),
                external_source=MediaExternalSource.ANILIST,
                title=AnilistNormalizer._get_title(media.title),
                format=media.format,
                genres=media.genres or [],
                status=AnilistNormalizer._convert_enum_field(media.status),
                cover_image=(
                    media.cover_image.extra_large if media.cover_image else None
                ),
                banner_image=media.banner_image,
                average_score=(
                    round(media.weighted_score / 10, 1) if media.weighted_score else None
                ),
                episodes=media.episodes,
                main_studio=AnilistNormalizer._get_main_studio(media.studios),
                chapters=media.chapters,
            )  # type: ignore
            media_list.append(mm)

        return media_list

    @staticmethod
    def _normalize_anilist_shared(media: AnilistMediaDetail) -> AniMediaData:
        """Normalize shared fields between minimal and detailed"""

        relations = AnilistNormalizer._normalize_relations(media.relations)
        recommendations = AnilistNormalizer._normalize_recommendations(
            media.recommendations
        )
        characters = AnilistNormalizer._normalize_characters(media.characters)

        start_date = AnilistNormalizer._convert_date(media.start_date)
        end_date = AnilistNormalizer._convert_date(media.end_date)

        return AniMediaData(
            id_mal=media.id_mal,
            title=AnilistNormalizer._build_title(media.title),
            format=AnilistNormalizer._convert_enum_field(media.format),
            genres=media.genres or [],
            status=MediaStatus(
                AnilistNormalizer._convert_enum_field(media.status)
                or MediaStatus.UNKNOWN.value
            ),
            cover_image=media.cover_image.extra_large if media.cover_image else None,
            description=strip_html(media.description),
            banner_image=media.banner_image,
            is_adult=media.is_adult,
            synonyms=media.synonyms or [],
            country_of_origin=media.country_of_origin,
            source=AnilistNormalizer._convert_enum_field(media.source),
            start_date=start_date,
            end_date=end_date,
            tags=(
                [MediaTag.model_validate(tag.model_dump()) for tag in media.tags]
                if media.tags
                else []
            ),
            relations=relations or [],
            recommendations=recommendations or [],
            characters=characters or [],
            trailer=AnilistNormalizer._convert_trailer_url(media.trailer),
            content_rating=None,
            background=None,
        )

    @staticmethod
    def normalize_anime_detail(media: AnilistMediaDetail) -> AnimeData:
        """Normalize AniList anime data to AnimeDetailed"""
        shared_data = AnilistNormalizer._normalize_anilist_shared(media)

        studios = AnilistNormalizer._normalize_studios(media.studios)

        return AnimeData(
            **shared_data.model_dump(),
            season=AnilistNormalizer._convert_enum_field(media.season),
            season_year=media.season_year,
            episodes=media.episodes,
            duration=media.duration,
            studios=studios,
            next_airing_episode=AnilistNormalizer._build_next_airing_episode(
                media.next_airing_episode
            ),
        )

    @staticmethod
    def normalize_manga_detail(media: AnilistMediaDetail) -> MangaData:
        """Normalize AniList manga data to MangaDetailed"""

        shared_data = AnilistNormalizer._normalize_anilist_shared(media)

        return MangaData(
            **shared_data.model_dump(),
            chapters=media.chapters,
            volumes=media.volumes,
        )

    @staticmethod
    def _normalize_relations(
        relations: Relations | None,
    ) -> List[MediaRelation] | None:
        """Extract common relations normalization"""
        if not relations:
            return None
        result = []
        for edge in relations.edges:

            cover_image = (
                edge.node.cover_image.extra_large if edge.node.cover_image else None
            )

            media_type = MediaType(edge.node.type)

            relation = MediaRelation(
                relation_type=AnilistNormalizer._convert_enum_field(edge.relation_type),
                id=edge.node.id,
                title=AnilistNormalizer._get_title(edge.node.title),
                format=AnilistNormalizer._convert_enum_field(edge.node.format),
                status=AnilistNormalizer._convert_enum_field(edge.node.status),
                cover_image=cover_image,
                media_type=media_type,
            )
            result.append(relation)

        return result

    @staticmethod
    def _normalize_recommendations(
        recommendations: Optional[Recommendations],
    ) -> Optional[List[MediaRecommendation]]:
        """Extract common recommendations normalization"""
        if not recommendations:
            return None
        result = []
        for edge in recommendations.edges:
            media_rec = edge.node.media_recommendation
            if media_rec is None:
                continue

            title = AnilistNormalizer._get_title(media_rec.title)

            cover_image = (
                media_rec.cover_image.extra_large if media_rec.cover_image else None
            )

            recommendation = MediaRecommendation(
                id=media_rec.id,
                title=title,
                cover_image=cover_image,
                media_type=MediaType(media_rec.type),
            )
            result.append(recommendation)

        return result

    @staticmethod
    def _normalize_characters(
        characters: Optional[Characters],
    ) -> Optional[List[MediaCharacter]]:
        """Extract common characters normalization
        return the url of the image
        """
        if not characters:
            return None

        result = []
        for edge in characters.edges:
            image = edge.node.image.large or ""

            name = edge.node.name.full

            voice_actor = None
            if edge.voice_actors:
                voice_actor = MediaVoiceActor(
                    image=edge.voice_actors[0].image.large or "",
                    name=edge.voice_actors[0].name.full,
                )

            character = MediaCharacter(
                role=AnilistNormalizer._convert_enum_field(edge.role),  # type: ignore
                image=image,
                name=name,
                voice_actor=voice_actor,
            )
            result.append(character)

        return result

    @staticmethod
    def _normalize_studios(studios: Optional[Studios]) -> Optional[List[MediaStudio]]:
        """Normalize studios (anime only)"""
        if not studios:
            return None

        return [
            MediaStudio(is_main=studio.is_main, name=studio.node.name)
            for studio in studios.edges
        ]

    @staticmethod
    def _build_title(title: Optional[Title]) -> MediaTitle:
        """Extract title with fallback logic"""
        if not title:
            return MediaTitle(title="", normalized="")
        raw_title = title.english or title.romaji or title.native or ""
        return MediaTitle(
            title=raw_title,
            normalized=normalize_title_text(raw_title),
            english=title.english,
            romaji=title.romaji,
            native=title.native,
        )

    @staticmethod
    def _get_main_studio(studios: Optional[Studios]) -> Optional[str]:
        """Get main studio name from studios"""
        if not studios:
            return None
        return next(
            (studio.node.name for studio in studios.edges if studio.is_main),
            None,
        )

    @staticmethod
    def _convert_date(date: Optional[MediaDate]) -> Optional[str]:
        if not date:
            return None
        parts = []
        if date.day:
            parts.append(f"{date.day:02d}")
        if date.month:
            parts.append(calendar.month_name[date.month])
        if date.year:
            parts.append(str(date.year))
        return " ".join(parts)

    @staticmethod
    def _convert_enum_field(text: Optional[str]) -> Optional[str]:
        """Convert UPPER_CASE or snake_case API enums to Title Case"""
        if not text:
            return None
        return " ".join(word.capitalize() for word in text.replace("_", " ").split())

    @staticmethod
    def _convert_trailer_url(
        trailer: Optional[AnilistTrailer],
    ) -> List[Trailer]:
        """Convert trailer URL to embeddable format if it's a YouTube link"""
        if not trailer:
            return []

        if trailer.site == "youtube" and trailer.id:
            url = f"https://www.youtube.com/watch?v={trailer.id}"
            thumbnail = trailer.thumbnail
            return [Trailer(url=url, thumbnail=thumbnail)]
        
        return []

    @staticmethod
    def _get_title(title: Optional[Title]) -> Optional[str]:
        """Extract best title string with fallback logic"""
        if not title:
            return None
        return title.english or title.romaji or title.native or None

    @staticmethod
    def _build_next_airing_episode(
        airing: Optional[NextAiringEpisode],
    ) -> Optional[UpcomingEpisode]:
        """Convert AniList's next airing episode to our common format"""
        if not airing or airing.airing_at is None:
            return None

        airing_datetime = datetime.fromtimestamp(
            airing.airing_at, tz=timezone.utc
        ).isoformat()
        return UpcomingEpisode(
            episode_number=airing.episode,
            airing_at=airing_datetime,
            season_number=None,
        )
