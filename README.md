# Equity Research API

An API service for generating equity research reports using LLM technology.

## Features
- Generate comprehensive equity research reports for companies
- Convert reports to PDF format
- API authentication
- Asynchronous task processing

## API Endpoints
- `/tasks`: Create a new task to generate a report.
- `/tasks/{task_id}`: Get the status of a task.
- `/reports/{task_id}`: Download the generated report.

## Tech Stack
- FastAPI for building the API
- Celery for asynchronous task processing
- Redis for task queue
- MySQL for storing task and report data
- Anthropic for generating reports
- WeasyPrint for converting reports to PDF format
## Environment Setup
1. You need to have a MySQL database installed on your local machine.
2. Run the following command to create a new conda environment and install the required packages
```zsh
conda create -n equity python=3.11 && conda activate equity && conda install fastapi uvicorn pymysql python-multipart celery redis-py toml anthropic markdown weasyprint python-jose  passlib
```
```zsh
conda activate equity
```
3. Run the following command to create a table in your MySQL database
```python
python app/database.py
```
## Run
1. Go to the project root directory
```zsh
cd dir/where/your/equity-research-agent
```
2. Start all the services in Mac (If you are using Windows, double click `start_services.bat`)
```bash
./start_services.sh
```
3. Send a post request using **curl**. Alternatively you can use Postman or Apifox.
```zsh
curl -X POST -H "Content-Type: application/json" \
     -d '{"company_id": "42601"}' \
     http://localhost:8000/tasks
```
4. Check task status
```zsh
curl -H "X-API-Key: your_api_key" http://localhost:8000/tasks/{task_id}
```
5. Download the generated report
```zsh
curl -H "X-API-Key: your_api_key" -o report.pdf http://localhost:8000/reports/{task_id}
```


28th Mar 2025:
TODO: JWT
