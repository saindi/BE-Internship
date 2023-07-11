from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import config

app = FastAPI()

origins = [
    f"http://localhost:5000",
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
        host=config.HOST,
        port=config.PORT
    )
