from typing import Optional
import logging

import redis.asyncio as redis
from redis.exceptions import RedisError
from app.core.config import settings

logger = logging.getLogger("careremind.cache")


class CacheClient:
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._available: bool = True

    @property
    def client(self) -> Optional[redis.Redis]:
        if self._client is None and self._available:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
            except Exception as e:
                logger.warning("Redis connection failed: %s", e)
                self._available = False
        return self._client

    async def get(self, key: str) -> Optional[str]:
        try:
            client = self.client
            if client:
                return await client.get(key)
        except RedisError as e:
            logger.warning("Redis get failed: %s", e)
        return None

    async def set(self, key: str, value: str, ex: int = 3600) -> bool:
        try:
            client = self.client
            if client:
                await client.set(key, value, ex=ex)
                return True
        except RedisError as e:
            logger.warning("Redis set failed: %s", e)
        return False

    async def delete(self, key: str) -> bool:
        try:
            client = self.client
            if client:
                await client.delete(key)
                return True
        except RedisError as e:
            logger.warning("Redis delete failed: %s", e)
        return False

    async def exists(self, key: str) -> bool:
        try:
            client = self.client
            if client:
                return await client.exists(key) > 0
        except RedisError as e:
            logger.warning("Redis exists failed: %s", e)
        return False

    async def incr(self, key: str) -> int:
        try:
            client = self.client
            if client:
                return await client.incr(key)
        except RedisError as e:
            logger.warning("Redis incr failed: %s", e)
        return 0

    async def expire(self, key: str, seconds: int) -> bool:
        try:
            client = self.client
            if client:
                await client.expire(key, seconds)
                return True
        except RedisError as e:
            logger.warning("Redis expire failed: %s", e)
        return False

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.close()
            except RedisError:
                pass


cache = CacheClient()
