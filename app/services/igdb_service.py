import logging
from app.integrations.igdb_api import IGDBApi
from app.models.igdb_models import IGDBGameDetail

logger = logging.getLogger(__name__)


class IGDBService:
    def __init__(self):
        self.api = IGDBApi()

    async def get_game_detail(self, game_id: int) -> IGDBGameDetail:
        """
        Service method to get game detail using IGDB API.
        Handles business logic, logging, and error handling.
        """
        try:
            logger.info(f"Service: Initiating game detail fetch for {game_id}")
            result = await self.api.get_game_detail(game_id)

            # Filter franchises.games: remove games where version_parent is None -> filter out bundles
            # game_type.type not in (1, filter out dlcs/addon
            # 3 -> filter out bundles
            # 5) -> filter out mods
            if result.franchises is not None:
                for franchise in result.franchises:
                    franchise.games = [
                        game
                        for game in franchise.games
                        if not (
                            game.version_parent is None
                            and game.game_type
                            and game.game_type.type not in (1, 3, 5)
                        )
                    ]

            logger.info(f"Service: Successfully retrieved and filtered game detail for {game_id}")
            return result
        except Exception as e:
            logger.error(f"Service: Failed to get game detail for {game_id}: {e}")
            raise
