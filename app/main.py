from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from log import logger
from config import global_settings
from user.router import router as user_router
from auth.router import router as auth_router
from company.router import router as company_router


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


app.include_router(auth_router, tags=["auth"])
app.include_router(user_router, tags=["user"])
app.include_router(company_router, tags=["company"])


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        reload=True,
        host=global_settings.host,
        port=global_settings.port
    )
