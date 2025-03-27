## Environment Setup
```zsh
conda create -n equity python=3.11 && conda activate equity && conda install fastapi uvicorn pymysql python-multipart celery redis-py toml
```
## Run
1. Start all the services in Mac (If you are using Windows, double click `start_services.bat`)
```bash
./start_services.sh
```

2. Send a post request using **curl**. Alternatively you can use Postman or Apifox
```zsh
curl -X POST -H "Content-Type: application/json" \
     -d '{"company_id": "AAPL"}' \
     http://localhost:8000/tasks
```
26th Mar 2025:
1.使用`config.py`统一了toml环境变量导入，可能imprt ModuleNotFoundError
2.`_load_financial_data`加入了financial.json数据加载，并将其加入到`build_prompt`中，untested
3.TODO:`tasks.py`LLM的httpx.post调用仍然未改进，是否直接调用`llm_service.py`中的`generate_report`函数？
4.TODO:convert Markdown format output to PDF?

修复LLM调用
# ... 现有代码 ...
# Generate report
llm = AnthropicService()
prompt = llm.build_prompt(company_data)
try:
    # 使用同步方式调用API
    import httpx
    response = httpx.post(
        f"{llm.base_url}/complete",
        json={
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "model": "claude-instant-1",
            "max_tokens_to_sample": 4000,
        },
        headers=llm.headers,
        timeout=120
    )
    response.raise_for_status()
    report_content = response.json().get("completion", "")
    
    if not report_content:
        raise ValueError("Empty response from LLM")


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