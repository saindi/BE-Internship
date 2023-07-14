from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from log import AppLogger
import config


logger = AppLogger.__call__().get_logger()

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


@app.on_event("startup")
async def startup_event():
    logger.info("App startup...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("App shutdown...")


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
        host=global_settings.host,
        port=global_settings.port
    )
