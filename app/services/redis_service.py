import json
from typing import Any, Optional

from redis.asyncio import Redis
import structlog

logger = structlog.get_logger("redis_service")


class RedisService:
    def __init__(self, redis_client: Redis):
        try:
            self.redis_client = redis_client
        except Exception as e:
            logger.error("redis_init_failed", error=str(e), exc_info=True)
            raise

    async def get_cached(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e), exc_info=True)
            raise

    async def set_cached(self, key: str, value: Any, ttl: int) -> None:
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(
                "redis_set_failed", key=key, ttl=ttl, error=str(e), exc_info=True
            )
            raise
