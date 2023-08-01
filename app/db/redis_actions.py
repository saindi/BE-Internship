import json
from datetime import timedelta

from db.redis import init_redis_pool


async def add_test_result_to_redis(result_id: int, user_id: int, id_company: int, id_quiz: int, data: dict):
    redis = await init_redis_pool()

    key = f"result_test:{result_id:}:id_user:{user_id}:id_company:{id_company}:id_quiz:{id_quiz}"

    await redis.setex(key, timedelta(hours=48), json.dumps(data))


async def get_value_by_keys(**kwargs):
    values = await get_values_by_keys(**kwargs)

    return None if len(values) == 0 else values[0]


async def get_values_by_keys(**kwargs):
    redis = await init_redis_pool()

    pattern = '*' + '*'.join([f"{key}:{value}" for key, value in kwargs.items()]) + '*'

    keys = await redis.keys(pattern)

    return await get_values(redis, keys)


async def get_values(redis, keys):
    return [json.loads(await redis.get(key)) for key in keys if await redis.get(key)]
