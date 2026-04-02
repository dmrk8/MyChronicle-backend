from turtle import st
from typing import List, Optional
import structlog
import calendar

from app.enums.user_media_entry_enums import MediaExternalSource, MediaType
from app.models.anilist_models import (
    AnilistMediaDetailed,
    AnilistMediaMinimal,
    MediaDate,
    Relations,
    Recommendations,
    Characters,
    Studios,
    Title,
)
from app.models.media_models import (
    AnimeDetailed,
    MangaDetailed,
    MediaCharacter,
    MediaMinimal,
    MediaRecommendation,
    MediaRelation,
    MediaStudio,
    MediaVoiceActor,
)

logger = structlog.get_logger("anilist_normalizer")


class AnilistNormalizer:

    @staticmethod
    def normalize_minimal(results: List[AnilistMediaMinimal]) -> List[MediaMinimal]:
        """Normalize AniList minimal media list"""
        media_list = []
        try:
            for media in results:
                mm = MediaMinimal(
                    id=media.id,
                    mediaType=media.type,
                    externalSource=MediaExternalSource.ANILIST,
                    title=AnilistNormalizer._get_title(media.title),
                    format=media.format,
                    genres=media.genres,
                    status=AnilistNormalizer._convert_enum_field(media.status),
                    coverImage=(
                        media.cover_image.extra_large if media.cover_image else None
                    ),
                    bannerImage=media.banner_image,
                    averageScore=(
                        round(media.average_score / 10, 1)
                        if media.average_score
                        else None
                    ),
                    episodes=media.episodes,
                    mainStudio=AnilistNormalizer._get_main_studio(media.studios),
                    chapters=media.chapters,
                )  # type: ignore
                media_list.append(mm)
        except Exception as e:
            logger.error("normalize_anilist_minimal", error=str(e))
        return media_list

    @staticmethod
    def normalize_anime_detailed(media: AnilistMediaDetailed) -> AnimeDetailed:
        """Normalize AniList anime data to AnimeDetailed"""
        logger.info("Normalizing anime detailed", media_id=media.id)
        try:
            relations = AnilistNormalizer._normalize_relations(media.relations)
            recommendations = AnilistNormalizer._normalize_recommendations(
                media.recommendations
            )
            characters = AnilistNormalizer._normalize_characters(media.characters)
            studios = AnilistNormalizer._normalize_studios(media.studios)

            start_date = AnilistNormalizer._convert_date(media.start_date)
            end_date = AnilistNormalizer._convert_date(media.end_date)

            return AnimeDetailed(
                id=media.id,
                externalSource=MediaExternalSource.ANILIST,
                mediaType=MediaType.ANIME,
                title=AnilistNormalizer._get_title(media.title),
                format=AnilistNormalizer._convert_enum_field(media.format),
                genres=media.genres,
                status=AnilistNormalizer._convert_enum_field(media.status),
                coverImage=media.cover_image.extra_large if media.cover_image else None,
                averageScore=(
                    round(media.average_score / 10, 1) if media.average_score else None
                ),
                description=media.description,
                bannerImage=media.banner_image,
                isAdult=media.is_adult,
                synonyms=media.synonyms,
                countryOfOrigin=media.country_of_origin,
                season=AnilistNormalizer._convert_enum_field(media.season),
                seasonYear=media.season_year,
                source=media.source,
                episodes=media.episodes,
                duration=media.duration,
                startDate=start_date,
                endDate=end_date,
                studios=studios,
                tags=media.tags,
                relations=relations,
                recommendations=recommendations,
                characters=characters,
                nextAiringEpisode=media.next_airing_episode,
            )
        except Exception as e:
            logger.error(
                "Error normalizing anime detailed", media_id=media.id, error=str(e)
            )
            raise

    @staticmethod
    def normalize_manga_detailed(media: AnilistMediaDetailed) -> MangaDetailed:
        """Normalize AniList manga data to MangaDetailed"""
        logger.info("Normalizing manga detailed", media_id=media.id)
        try:
            relations = AnilistNormalizer._normalize_relations(media.relations)
            recommendations = AnilistNormalizer._normalize_recommendations(
                media.recommendations
            )
            characters = AnilistNormalizer._normalize_characters(media.characters)
            start_date = AnilistNormalizer._convert_date(media.start_date)
            end_date = AnilistNormalizer._convert_date(media.end_date)

            return MangaDetailed(
                id=media.id,
                externalSource=MediaExternalSource.ANILIST,
                mediaType=MediaType.MANGA,
                title=AnilistNormalizer._get_title(media.title),
                format=AnilistNormalizer._convert_enum_field(media.format),
                genres=media.genres,
                status=media.status,
                coverImage=media.cover_image.extra_large if media.cover_image else None,
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
                startDate=start_date,
                endDate=end_date,
                tags=media.tags,
                relations=relations,
                recommendations=recommendations,
                characters=characters,
            )
        except Exception as e:
            logger.error(
                "Error normalizing manga detailed", media_id=media.id, error=str(e)
            )
            raise

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
                relationType=AnilistNormalizer._convert_enum_field(edge.relation_type),
                id=edge.node.id,
                title=AnilistNormalizer._get_title(edge.node.title),
                format=AnilistNormalizer._convert_enum_field(edge.node.format),
                status=AnilistNormalizer._convert_enum_field(edge.node.status),
                coverImage=cover_image,
                mediaType=media_type,
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
                coverImage=cover_image,
                mediaType=MediaType(media_rec.type),
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
                role=AnilistNormalizer._convert_enum_field(edge.role), # type: ignore
                image=image,
                name=name,
                voiceActor=voice_actor,
            )
            result.append(character)

        return result

    @staticmethod
    def _normalize_studios(studios: Studios) -> Optional[List[MediaStudio]]:
        """Normalize studios (anime only)"""
        if not studios:
            return None

        return [
            MediaStudio(isMain=studio.is_main, name=studio.node.name)
            for studio in studios.edges
        ]

    @staticmethod
    def _get_title(title: Title) -> str:
        """Extract title with fallback logic"""
        return title.english or title.romaji or title.native or ""

    @staticmethod
    def _get_main_studio(studios: Studios) -> Optional[str]:
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
