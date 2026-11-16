from typing import Optional
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeData, MALMangaData
from app.models.providers.omdb_models import OMDbData
from app.models.db.media_core_models import (
    ExternalReference,
    MediaDBUpsert,
)
from app.enums.media_enums import MediaExternalSource, MediaType

from app.models.providers.tmdb_models import TMDBTVDetail, TMDBMovieDetail


class MediaDBNormalizer:
    @staticmethod
    def normalize_ani(
        media: AnilistMediaDetail,
        mal_data: Optional[MALAnimeData | MALMangaData] = None,
    ) -> MediaDBUpsert:
        external_ids = [
            ExternalReference(
                id=str(media.id),
                source=MediaExternalSource.ANILIST,
            ),
        ]

        if mal_data:
            external_ids.append(
                ExternalReference(
                    id=str(mal_data.id),
                    source=MediaExternalSource.MAL,
                )
            )

        return MediaDBUpsert(
            primary_external_id=str(media.id),
            primary_external_source=MediaExternalSource.ANILIST,
            media_type=MediaType[media.type.upper()],
            external_ids=external_ids,
        )

    @staticmethod
    def normalize_tv(tv: TMDBTVDetail, omdb_data: Optional[OMDbData]) -> MediaDBUpsert:
        external_ids = [
            ExternalReference(
                id=str(tv.id),
                source=MediaExternalSource.TMDB,
            )
        ]

        if omdb_data and omdb_data.imdbID:
            external_ids.append(
                ExternalReference(
                    id=omdb_data.imdbID,
                    source=MediaExternalSource.OMDB,
                )
            )

        return MediaDBUpsert(
            primary_external_id=str(tv.id),
            primary_external_source=MediaExternalSource.TMDB,
            media_type=MediaType.TV,
            external_ids=external_ids,
        )

    @staticmethod
    def normalize_movie(
        movie: TMDBMovieDetail, omdb_data: Optional[OMDbData] = None
    ) -> MediaDBUpsert:
        external_ids = [
            ExternalReference(
                id=str(movie.id),
                source=MediaExternalSource.TMDB,
            )
        ]
        if omdb_data and omdb_data.imdbID:
            external_ids.append(
                ExternalReference(
                    id=(omdb_data.imdbID),
                    source=MediaExternalSource.OMDB,
                )
            )

        return MediaDBUpsert(
            primary_external_id=str(movie.id),
            primary_external_source=MediaExternalSource.TMDB,
            media_type=MediaType.MOVIE,
            external_ids=external_ids,
        )
