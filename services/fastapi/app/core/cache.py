"""
Redis cache client — Upstash TLS-aware.

Upstash requires TLS (rediss:// scheme). We detect this via
settings.redis_is_tls and pass the appropriate ssl kwargs so that
redis.asyncio validates the server certificate rather than skipping it.

All operations degrade gracefully: if Redis is unreachable the method
returns None / False / 0 and logs a WARNING — the API continues serving.
"""

from typing import Optional
import logging
import ssl

import redis.asyncio as redis
from redis.exceptions import RedisError
from app.core.config import settings

logger = logging.getLogger("careremind.cache")


def _build_redis_client() -> redis.Redis:
    """
    Factory that creates a redis.asyncio.Redis instance with the correct
    TLS settings for Upstash.

    Upstash requires:
      - scheme:          rediss:// (TLS)
      - ssl_cert_reqs:   required  (validate the server certificate)
    """
    extra: dict = {
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
    }

    if settings.redis_is_tls:
        # ssl.CERT_REQUIRED tells the Redis client to validate the server's
        # certificate against the system CA bundle — mandatory for production.
        extra["ssl_cert_reqs"] = ssl.CERT_REQUIRED

    return redis.from_url(settings.UPSTASH_REDIS_URL, **extra)


class CacheClient:
    """
    Thin async wrapper around redis.asyncio with lazy initialisation and
    graceful degradation.  All public methods are safe to call even when
    Redis is temporarily unavailable — they return a sentinel value and
    emit a WARNING log rather than propagating the exception.
    """

    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None
        self._available: bool = True

    @property
    def client(self) -> Optional[redis.Redis]:
        if self._client is None and self._available:
            try:
                self._client = _build_redis_client()
            except Exception as exc:
                logger.warning(
                    "Redis client initialisation failed — cache disabled",
                    extra={"error": str(exc), "redis_url_scheme": settings.UPSTASH_REDIS_URL.split(":")[0]},
                )
                self._available = False
        return self._client

    # ── Read ──────────────────────────────────────────────────────────────

    async def get(self, key: str) -> Optional[str]:
        try:
            client = self.client
            if client:
                return await client.get(key)
        except RedisError as exc:
            logger.warning("Redis GET failed", extra={"key": key, "error": str(exc)})
        return None

    async def exists(self, key: str) -> bool:
        try:
            client = self.client
            if client:
                return await client.exists(key) > 0
        except RedisError as exc:
            logger.warning("Redis EXISTS failed", extra={"key": key, "error": str(exc)})
        return False

    # ── Write ─────────────────────────────────────────────────────────────

    async def set(self, key: str, value: str, ex: int = 3600) -> bool:
        try:
            client = self.client
            if client:
                await client.set(key, value, ex=ex)
                return True
        except RedisError as exc:
            logger.warning("Redis SET failed", extra={"key": key, "error": str(exc)})
        return False

    async def delete(self, key: str) -> bool:
        try:
            client = self.client
            if client:
                await client.delete(key)
                return True
        except RedisError as exc:
            logger.warning("Redis DELETE failed", extra={"key": key, "error": str(exc)})
        return False

    async def incr(self, key: str) -> int:
        try:
            client = self.client
            if client:
                return await client.incr(key)
        except RedisError as exc:
            logger.warning("Redis INCR failed", extra={"key": key, "error": str(exc)})
        return 0

    async def expire(self, key: str, seconds: int) -> bool:
        try:
            client = self.client
            if client:
                await client.expire(key, seconds)
                return True
        except RedisError as exc:
            logger.warning("Redis EXPIRE failed", extra={"key": key, "error": str(exc)})
        return False

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.aclose()
            except RedisError:
                pass
            finally:
                self._client = None


# Singleton — imported by the rest of the application.
cache = CacheClient()
