from typing import Optional
from uuid import UUID

import redis.asyncio as redis

from app.core.config import settings
from app.domain.interfaces import TokenRepository


class RedisTokenRepository(TokenRepository):
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_CACHE_URL, encoding="utf-8", decode_responses=True
        )

    async def add_to_blacklist(self, token: str, expires_in: int) -> None:
        key = f"blacklist:{token}"

        await self.redis.setex(key, expires_in, "logged_out")

    async def is_blacklisted(self, token: str) -> bool:
        key = f"blacklist:{token}"
        value = await self.redis.get(key)
        return value is not None

    async def close(self):
        await self.redis.close()

    async def save_refresh_token(
        self, token: str, user_id: UUID, expires_in: str
    ) -> None:
        key = f"refresh:{token}"
        await self.redis.setex(key, expires_in, str(user_id))

    async def get_refresh_token_user_id(self, token: str) -> Optional[str]:
        key = f"refresh:{token}"
        return await self.redis.get(key)

    async def delete_refresh_token(self, token: str) -> None:
        key = f"refresh:{token}"
        await self.redis.delete(key)
