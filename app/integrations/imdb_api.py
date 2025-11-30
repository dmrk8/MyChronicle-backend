import httpx
from app.models.imdb_models import IMDBResponse


class IMDBApi:
    def __init__(self):
        self.base_url = "https://imdb.iamidiotareyoutoo.com/search"

    async def get_movie_data(self, imdb_id: str) -> IMDBResponse:
        """Fetch movie data from IMDB API."""
        url = f"{self.base_url}?tt={imdb_id}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return IMDBResponse(**response.json())
