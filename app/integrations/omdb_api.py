import httpx
from typing import Optional
from app.models.api.omdb_models import OMDbData

OMDB_API_URL = "http://www.omdbapi.com/"


class OMDbApi:
    def __init__(self, api_key: str, client: httpx.AsyncClient):
        self.api_key = api_key
        self.BASE_URL = OMDB_API_URL
        self.client = client

    async def fetch_data(
        self, title: Optional[str] = None, imdb_id: Optional[str] = None
    ) -> Optional[OMDbData]:
        params = {"apikey": self.api_key}
        if title:
            params["t"] = title
        if imdb_id:
            params["i"] = imdb_id
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "True":
            return OMDbData.model_validate(data)
        return None
