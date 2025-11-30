import logging
from app.integrations.imdb_api import IMDBApi
from app.models.imdb_models import IMDBAggregateRating

logger = logging.getLogger(__name__)


class IMDBService:
    def __init__(self):
        self.api = IMDBApi()

    async def get_imdb_rating(self, imdb_id: str) -> IMDBAggregateRating:
        """Service method to get IMDB rating data."""
        try:
            logger.info(f"IMDBService: Fetching rating for {imdb_id}")
            response = await self.api.get_movie_data(imdb_id)
            if response.short.aggregate_rating:
                return response.short.aggregate_rating
            else:
                raise ValueError("No aggregate rating available")
        except Exception as e:
            logger.error(f"IMDBService: Failed to get rating for {imdb_id}: {e}")
            raise
