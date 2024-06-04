from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from log import logger
from config import global_settings
from tasks import apscheduler_tasks
from user.routers.crud import router as user_crud_router
from user.routers.actions import router as user_actions_router
from auth.router import router as auth_router
from company.routers.crud import router as company_crud_router
from company.routers.actions import router as company_actions_router
from quiz.routers.quiz import router as quiz_crud_router
from quiz.routers.question import router as question_crud_router


app = FastAPI()

origins = [
    "http://localhost:5000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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

    apscheduler_tasks.scheduler.start()


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


app.include_router(auth_router, tags=["Auth"])

app.include_router(user_crud_router, tags=["User"])
app.include_router(user_actions_router, tags=["User actions"])

app.include_router(company_crud_router, tags=["Company"])
app.include_router(company_actions_router, tags=["Company actions"])

app.include_router(quiz_crud_router, tags=["Quiz"])

app.include_router(question_crud_router, tags=["Question"])


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        reload=True,
        host=global_settings.host,
        port=global_settings.port
    )
