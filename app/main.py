import os
from fastapi import FastAPI, status
import uvicorn
from dotenv import load_dotenv

app = FastAPI()


@app.get("/")
async def health_check():
    return {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working"
    }


if __name__ == "__main__":
    load_dotenv()

    uvicorn.run(
        'main:app',
        reload=True,
        host=os.environ.get("HOST"),
        port=int(os.environ.get("PORT"))
    )
