from fastapi import FastAPI, status
import uvicorn

import config

app = FastAPI()


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
