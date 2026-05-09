from typing import TypeVar, Optional
from pydantic import BaseModel
from redis.asyncio import Redis
import structlog


T = TypeVar("T", bound=BaseModel)

logger = structlog.get_logger()


class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.logger = logger.bind(service="RedisService")

    async def get_cached(   
        self,
        key: str,
        endpoint: str,
        service: str,
        cache_type: str,
        model: type[T],
    ) -> Optional[T]:
        try:
            data = await self.redis_client.get(key)

            if data:
                self.logger.info(
                    "redis_cache_hit",
                    key=key,
                    endpoint=endpoint,
                    service=service,
                    cache_type=cache_type,
                )
                return model.model_validate_json(data)
            else:
                self.logger.info(
                    "redis_cache_miss",
                    key=key,
                    endpoint=endpoint,
                    service=service,
                    cache_type=cache_type,
                )
                return None
        except Exception as e:
            self.logger.error("redis_get_failed", key=key, error=str(e), exc_info=True)
            raise

    async def set_cached(self, key: str, value: BaseModel, ttl: int = 3600) -> None:
        try:
            await self.redis_client.setex(key, ttl, value.model_dump_json())
        except Exception as e:
            self.logger.error(
                "redis_set_failed", key=key, ttl=ttl, error=str(e), exc_info=True
            )
            raise
