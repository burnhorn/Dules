import redis.asyncio as redis
from app.domain.interfaces import TokenRepository
from app.core.config import settings

class RedisTokenRepository(TokenRepository):
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def add_to_blacklist(self, token: str, expries_in: int) -> None:
        key = f"blacklist:{token}"

        await self.redis.setex(key, expries_in, "logged_out")

    async def is_blacklisted(self, token: str) -> bool:
        key = f"blacklist:{token}"
        value = await self.redis.get(key)
        return value is not None
    
    async def close(self):
        await self.redis.close()