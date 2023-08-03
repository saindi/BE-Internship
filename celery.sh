#!/bin/bash

cd app

if [[ "${1}" == "celery_worker" ]]; then
  celery --app=tasks.celery_tasks:celery worker -l INFO
elif [[ "${1}" == "celery_beat" ]]; then
  celery --app=tasks.celery_tasks:celery beat -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=tasks.celery_tasks:celery flower
 fi