from httpx import AsyncClient

from app.integrations.http_helpers import perform_request
from app.models.providers.mal_models import MALAnimeData, MALMangaData

MAL_URL = "https://api.myanimelist.net/v2"
MAL_FIELDS = (
    "mean,rank,popularity,num_list_users," "num_scoring_users,rating,background"
)


class MALApi:
    def __init__(self, client_id: str, client: AsyncClient):
        self.client_id = client_id
        self.client = client

    @property
    def headers(self) -> dict[str, str]:
        return {"X-MAL-CLIENT-ID": self.client_id}

    async def get_anime_details(self, mal_id: int) -> MALAnimeData:
        data = await perform_request(
            client=self.client,
            method="GET",
            url=f"{MAL_URL}/anime/{mal_id}",
            headers=self.headers,
            params={"fields": MAL_FIELDS},
            action="get_anime_details",
        )
        return MALAnimeData.model_validate(data)

    async def get_manga_details(self, mal_id: int) -> MALMangaData:
        data = await perform_request(
            client=self.client,
            method="GET",
            url=f"{MAL_URL}/manga/{mal_id}",
            headers=self.headers,
            params={"fields": MAL_FIELDS},
            action="get_manga_details",
        )
        return MALMangaData.model_validate(data)
