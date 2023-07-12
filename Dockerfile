FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY ./app .
COPY requirements.txt .
COPY .env-docker .
COPY ./tests ./tests

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]