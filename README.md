## Environment Setup
```zsh
conda create -n equity python=3.11 && conda activate equity && conda install fastapi uvicorn pymysql python-multipart celery redis-py toml
```

26th Mar 2025:
1.使用`config.py`统一了toml环境变量导入，可能imprt ModuleNotFoundError
2.`_load_financial_data`加入了financial.json数据加载，并将其加入到`build_prompt`中，untested
3.TODO:`tasks.py`LLM的httpx.post调用仍然未改进，是否直接调用`llm_service.py`中的`generate_report`函数？
4.TODO:convert Markdown format output to PDF?