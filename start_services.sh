#!/bin/bash
# Quick Start Script for Mac

# Define the name of your conda environment
CONDA_ENV="equity"

# Launch FastAPI application in a new Terminal tab
osascript -e 'tell application "Terminal" to activate' -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
sleep 1
osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && conda activate ${CONDA_ENV} && uvicorn app.main:app --reload\" in selected tab of the front window"
echo "FastAPI application started..."

# Launch Celery Worker in another new Terminal tab
osascript -e 'tell application "Terminal" to activate' -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
sleep 1
osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && conda activate ${CONDA_ENV} && celery -A app.celery_config.celery worker --loglevel=info\" in selected tab of the front window"
echo "Celery Worker started..."

echo "All services launched!"