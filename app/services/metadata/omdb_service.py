import structlog
from typing import Optional

from app.integrations.omdb_api import OMDbApi
from app.models.providers.omdb_models import OMDbData

logger = structlog.get_logger()


class OMDbService:
    def __init__(self, omdb_api: OMDbApi):
        self.omdb_api = omdb_api

    async def fetch_data(
        self, title: Optional[str] = None, imdb_id: Optional[str] = None
    ) -> Optional[OMDbData]:
        try:
            return await self.omdb_api.fetch_data(
                title=title,
                imdb_id=imdb_id,
            )
        except ValueError as exc:
            logger.warning(
                "omdb_data_unavailable",
                imdb_id=imdb_id,
                title=title,
                error=str(exc),
            )
            return None
