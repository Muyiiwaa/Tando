from typing import Any, Optional
import json
from datetime import timedelta
import redis.asyncio as redis
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.default_ttl = timedelta(hours=24)

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        if ttl is None:
            ttl = self.default_ttl
        await self.redis.setex(
            key,
            int(ttl.total_seconds()),
            json.dumps(value)
        )

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    def get_key(self, *parts: str) -> str:
        return ":".join(str(part) for part in parts) 