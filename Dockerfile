FROM python:3.11

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]