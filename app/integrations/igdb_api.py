import os
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import httpx
from app.models.igdb_models import IGDBGameDetail, IGDBToken

load_dotenv()

logger = logging.getLogger(__name__)


class IGDBApi:
    BASE_URL = "https://api.igdb.com/v4"
    TOKEN_URL = "https://id.twitch.tv/oauth2/token"

    def __init__(self):
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_in = None
        self.client = httpx.AsyncClient(timeout=10.0) 

    @property
    def headers(self) -> Dict[str, str]:
        if not (self.access_token and self.client_id):
            raise ValueError("Access token or client id not available.")
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    async def get_access_token(self) -> IGDBToken:
        """
        Fetches a new access token from Twitch for IGDB API.
        """
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "IGDB_CLIENT_ID and IGDB_CLIENT_SECRET must be set in environment variables"
            )

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        try:
            logger.info("Fetching IGDB access token")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.TOKEN_URL, params=params)
                response.raise_for_status()
                data = response.json()

                result = IGDBToken.model_validate(data)
                logger.info("Successfully fetched IGDB access token")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching IGDB token: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching IGDB token: {str(e)}")
            raise
        except KeyError as e:
            logger.error(f"Missing key in token response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching IGDB token: {str(e)}")
            raise

    async def get_game_detail(self, game_id: int) -> IGDBGameDetail:
        """
        Fetches detailed information for a specific game from IGDB.
        """
        # Ensure access token is available
        if not self.access_token:
            await self.get_access_token()

        url = f"{self.BASE_URL}/games"
        body = f"""
        fields
        aggregated_rating,
        aggregated_rating_count,
        alternative_names.name,
        artworks.url,
        cover.url,
        first_release_date,
        franchises.name,
        franchises.games.name,
        franchises.games.game_type.type,
        franchises.games.version_parent,
        game_modes.name,
        game_type.type,
        genres.id,
        genres.name,
        involved_companies.company.name,
        involved_companies.developer,
        keywords.name,
        multiplayer_modes.*,
        name,
        platforms.name,
        player_perspectives.name,
        storyline,
        summary,
        themes.name,
        total_rating,
        total_rating_count;
        where id = {game_id};
        limit 1;
        """

        try:
            logger.info(f"Fetching game detail for ID: {game_id}")
            response = await self.client.post(
                url, headers=self.headers, content=body
            )  # Reuse client
            response.raise_for_status()
            data = response.json()

            if not data:
                raise ValueError(f"No game found with ID {game_id}")

            # Map to IGDBGameDetail model
            game_detail = IGDBGameDetail.model_validate(data[0])

            logger.info(f"Successfully fetched game detail for {game_id}")
            return game_detail

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching game detail: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error fetching game detail: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Validation or data error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching game detail: {str(e)}")
            raise

    # Add a close method if needed (e.g., in FastAPI lifespan)
    async def close(self):
        await self.client.aclose()
