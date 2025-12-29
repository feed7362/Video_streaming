import random
import time
from typing import Optional

from cachetools import TTLCache
from redis.asyncio import Redis


class RateLimiter:
    LUA_SCRIPT = """
    redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, ARGV[2])
    local count = redis.call("ZCARD", KEYS[1])
    if count >= tonumber(ARGV[3]) then
        return 1
    end
    redis.call("ZADD", KEYS[1], ARGV[1], ARGV[5])
    redis.call("EXPIRE", KEYS[1], ARGV[4])
    return 0
    """

    def __init__(self, redis: Redis):
        self._redis = redis
        self._lua_sha = None
        # Stores up to 10,000 blocked IPs.
        # Items expire automatically based on the 'window_seconds'
        self._local_block_cache: TTLCache = TTLCache(
            maxsize=10_000,
            ttl=60,
        )

    async def _get_script_sha(self) -> Optional[str]:
        if self._lua_sha is None:
            self._lua_sha = await self._redis.script_load(self.LUA_SCRIPT)
        return self._lua_sha

    async def is_limited(
        self,
        ip_address: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        cache_key = f"{endpoint}:{ip_address}"

        if self._local_block_cache.get(cache_key):
            # We already know ip is blocked, so no need to talk to Redis.
            return True

        sha = await self._get_script_sha()
        current_ms = int(time.time() * 1000)
        window_start_ms = current_ms - (window_seconds * 1000)
        member_id = f"{current_ms}-{random.randint(0, 100000)}"

        is_blocked_in_redis = await self._redis.evalsha(
            sha,
            1,
            f"rate_limit:{cache_key}",  # Redis Key
            current_ms,
            window_start_ms,
            max_requests,
            window_seconds,
            member_id,
        )

        if is_blocked_in_redis == 1:
            self._local_block_cache[cache_key] = True

            return True

        return False
