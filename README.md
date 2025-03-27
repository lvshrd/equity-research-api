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
conda create -n equity python=3.11 && conda activate equity && conda install fastapi uvicorn pymysql python-multipart celery redis-py toml anthropic
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
TODO:convert Markdown format output to PDF?
```python
# ... 现有代码 ...
# 在文件顶部添加
from weasyprint import HTML
import tempfile

# 在保存报告部分
# Save report
report_dir = "reports"
os.makedirs(report_dir, exist_ok=True)
report_filename = f"{task_id}_{company_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
report_path = os.path.join(report_dir, report_filename)

# 先保存为HTML
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Equity Research Report - {company_data['metadata']['company_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
    </style>
</head>
<body>
    {report_content}
</body>
</html>
"""

# 使用weasyprint转换为PDF
HTML(string=html_content).write_pdf(report_path)
# ... 现有代码 ...
```