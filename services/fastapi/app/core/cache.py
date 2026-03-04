import redis
from app.core.config import settings


class CacheClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL)

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value: str, ex: int = 3600):
        self.client.set(key, value, ex=ex)

    def delete(self, key: str):
        self.client.delete(key)


cache = CacheClient()
