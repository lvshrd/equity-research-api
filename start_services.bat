@echo off
start cmd /k "conda activate equity && uvicorn app.main:app --reload"
start cmd /k "conda activate equity && celery -A app.celery_config.celery worker --loglevel=info"
echo All services launched!