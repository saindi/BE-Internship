import json
from datetime import timedelta

import redis.asyncio as redis

from config import global_settings


async def init_redis_pool() -> redis.Redis:
    redis_c = await redis.from_url(global_settings.redis_url)
    return redis_c


async def add_test_result_to_redis(result_id: int, user_id, data: dict):
    redis = await init_redis_pool()

    key = f"result_test:{result_id:}:id_user:{user_id}"

    await redis.setex(key, timedelta(hours=48), json.dumps(data))


async def get_result_from_redis(result_id: int, user_id: int):
    redis = await init_redis_pool()

    data = await redis.get(f"result_test:{result_id}:id_user:{user_id}")

    return json.loads(data) if data else None
