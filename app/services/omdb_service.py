import structlog
from typing import Optional
from app.integrations.omdb_api import OMDbApi
from app.models.api.omdb_models import OMDbData

logger = structlog.get_logger()

class OMDbService:
    def __init__(self, omdb_api: OMDbApi):
        self.omdb_api = omdb_api
        self.logger = logger.bind(service="OMDbService")

    async def fetch_data(
        self, title: Optional[str] = None, imdb_id: Optional[str] = None
    ) -> Optional[OMDbData]:
        self.logger.info("fetch_data_called", title=title, imdb_id=imdb_id)
        return await self.omdb_api.fetch_data(title=title, imdb_id=imdb_id)