from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_models
from db.redis import init_redis_pool
import uvicorn

import config

app = FastAPI()

origins = [
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    # test db
    await init_models()

    # test redis
    redis = await init_redis_pool()
    await redis.set('a', 10)
    value = await redis.get('a')
    print(value)

    return {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working"
    }


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        reload=True,
        host=config.HOST,
        port=config.PORT
    )
