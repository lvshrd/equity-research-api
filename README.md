# Equity Research API

An API service for generating equity research reports combining AI analysis with financial data pipelines. This is the technical assessment project from AIDF (Asian Institute of Digital Finance). 

## Features
- **AI-Powered Analysis**: Claude-3 Haiku etc. model for financial reasoning
- **Data Integration**: Real-time market data + fundamental analysis
- **Automated Workflows**: Celery task queue with Redis backend
- **Multi-Format Output**: Markdown reports storage and HTML PDF format conversion for viewing and downloading
- **User Authentication**: API authentication with api_key and JWT token. 

## API Endpoints
| Method | Endpoint             | Description                                                    |
|--------|----------------------|----------------------------------------------------------------|
| POST   | `/tasks`             | Create a new task to let agent to generate a report.           |
| GET    | `/tasks`             | Retrieve all report generation tasks list.                     |
| GET    | `/tasks/{task_id}`   | Get the status of a specific task.                             |
| GET    | `/reports/{task_id}/view` | View the generated report in HTML format.                      |
| GET    | `/reports/{task_id}` | Download the generated report from a certain task.             |
| POST   | `/token`             | Allows valid users to obtain a JWT token by providing username and password. |

You can click [here](docs/example_report.html) to view the example demo report generated for American Airlines Group.

## Tech Stack
- FastAPI for building the API
- Celery for asynchronous task processing
- Redis for task queue
- MySQL for storing task and report data
- Langchain Agentic framework and Anthropic for agentic reports tasks
- Two function tool including fetch data from **Yahoo** and local json data.
## Getting Started 🚀
### Prerequisites
- Python 3.11 with conda
- MySQL Server
- Redis Server
- Anthropic API key

### Environment Setup
1. Clone this repository to your local machine
```zsh
git clone https://github.com/lvshrd/equity-research-api.git
```
```zsh
cd equity-research-api
```
2. Run the following command to create a new conda environment and install the required packages
```zsh
conda create -n equity python=3.11 && conda activate equity && conda install fastapi uvicorn pymysql python-multipart celery redis-py toml anthropic markdown weasyprint python-jose  passlib yfinance pandas langchain langgraph langchain_anthropic
```
3. Edit the configuration file [config.toml](config/config_example.toml) with your own settings.
4. Run the following command to create users and tasks tables in your MySQL database and insert default user.
```python
python app/database.py
```
### Run
1. Go to the project root directory
```zsh
cd dir/where/your/equity-research-api
```
2. Start all the services in Mac (If you are using Windows, double click `start_services.bat`)
```bash
./start_services.sh
```
3. Next, you can call these api by using your custom api key defined in [config.toml](config/config_example.toml).  Through FastAPI [Interactive API docs](http://127.0.0.1:8000/docs#) provided by Swagger UI to test is highly recommended.

<p align="center">
  <img src="docs/FastAPI_docs.png" alt="FastAPI interactive API documentation" width="80%">
</p>

4. Alternatively, you could use postman, firefox or any other tools, where `/token` api is used for JWT or simply put your api key in header of your request.

## Development Guide
### Project Structure
```
equity-research-api/
├── app/
│   ├── agents/  # AI Agent implementations
│   │   ├──tools/  # Custom Function tools for Agent
│   │   └──research_agent.py
│   ├── tasks/   # Celery task exclusively for report generation
│   ├── main.py  # FastAPI entry point
│   ├── auth.py  # Authentication and authorization
│   ├── data_loader.py  # Data loader for data folder
│   ├── database.py # Database connection and setup
│   ├── models.py # Pydantic models for data validation
│   └── utils.py # PDF conversion
├── data/
├── config/
```
## Adding New Data Tools

1. Create new tool class in app/tools/
2. Implement required interface:
```python
class FinancialTool(BaseTool):
    name = "earning_analysis"
    description = "Analyzes company earnings reports"
    
    def _run(self, symbol: str) -> dict:
        # Implementation here
 ```