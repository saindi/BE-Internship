import redis.asyncio as redis

from main import global_settings


async def init_redis_pool() -> redis.Redis:
    redis_c = await redis.from_url(global_settings.redis_url)
    return redis_c
