from httpx import AsyncClient

from app.integrations.http_helpers import perform_request
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse

JIKAN_URL = "https://api.jikan.moe/v4"


class JikanAPI:
    def __init__(self, client: AsyncClient):
        self.client = client


    async def get_anime_details(self, mal_id: int) -> MALAnimeResponse:
        url = f"{JIKAN_URL}/anime/{mal_id}"
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=None,
            action="get_anime_details",
        )  
        return MALAnimeResponse.model_validate(data)
       
    
    async def get_manga_details(self, mal_id: int) -> MALMangaResponse:
        url = f"{JIKAN_URL}/manga/{mal_id}"
        data = await perform_request(
            client=self.client,
            method="GET",
            url=url,
            headers=None,
            action="get_manga_details",
        )  
        return MALMangaResponse.model_validate(data) 
       