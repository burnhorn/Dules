from typing import Optional

import redis.asyncio as redis

from app.core.config import settings
from app.domain.interfaces import CacheRepository


class RedisCacheRepository(CacheRepository):
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """
        특정 패턴의 키를 찾아 모두 삭제
        """
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)
