FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY ./app .
COPY requirements.txt .
COPY .env .
COPY ./tests ./tests
COPY app.sh .

RUN pip install -r requirements.txt