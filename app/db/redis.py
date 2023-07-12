import redis.asyncio as redis
from config import REDIS_HOST, REDIS_PORT


async def init_redis_pool() -> redis.Redis:
    redis_c = await redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    return redis_c
