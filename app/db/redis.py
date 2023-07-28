import json
from datetime import timedelta

import redis.asyncio as redis

from config import global_settings


async def init_redis_pool() -> redis.Redis:
    redis_c = await redis.from_url(global_settings.redis_url)
    return redis_c


async def add_test_result_to_redis(result_id: int, data: dict):
    redis = await init_redis_pool()

    key = f"result_test:{result_id}"

    await redis.setex(key, timedelta(hours=48), json.dumps(data))
