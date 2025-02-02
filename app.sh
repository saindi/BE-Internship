#!/bin/bash

sleep 15

alembic upgrade head

cd app

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000