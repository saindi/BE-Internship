from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_models
from db.redis import init_redis_pool
import uvicorn

import config


app = FastAPI()

global_settings = config.Settings()


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
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working"
    }


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        reload=True,
        host=global_settings.HOST,
        port=global_settings.PORT
    )
