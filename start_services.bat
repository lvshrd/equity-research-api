@echo off
start cmd /k "conda activate equity && uvicorn app.main:app --reload"
start cmd /k "conda activate equity && celery -A config.celery_config.celery_app worker --loglevel=info"
echo All services launched!