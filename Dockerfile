FROM python:3.11

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY . .

RUN pip install -r requirements.txt

RUN chmod a+x *.sh