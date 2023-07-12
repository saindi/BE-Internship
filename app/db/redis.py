import redis.asyncio as redis

import config

global_settings = config.Settings()


async def init_redis_pool() -> redis.Redis:
    redis_c = await redis.from_url(global_settings.REDIS_URL)
    return redis_c
