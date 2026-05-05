import httpx
from typing import Optional
from app.integrations.http_helpers import perform_request
from app.models.providers.omdb_models import OMDbData

OMDB_API_URL = "http://www.omdbapi.com/"


class OMDbApi:
    def __init__(self, api_key: str, client: httpx.AsyncClient):
        self.api_key = api_key
        self.BASE_URL = OMDB_API_URL
        self.client = client

    async def fetch_data(
        self, title: Optional[str] = None, imdb_id: Optional[str] = None
    ) -> OMDbData:
        params = {"apikey": self.api_key}
        if title:
            params["t"] = title
        if imdb_id:
            params["i"] = imdb_id
        data = await perform_request(
            client=self.client,
            method="GET",
            url=self.BASE_URL,
            params=params,
            headers=None,
            action="fetch_omdb_data",
        )
        if data.get("Response") == "False":
            raise ValueError(data.get("Error", "Unknown error from OMDb API"))

        return OMDbData.model_validate(data)
