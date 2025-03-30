# app/tasks.py
from config.celery_config import celery_app
from app.database import get_db_connection
from datetime import datetime
import os
from config.config_load import CONFIG
import asyncio
from app.agents.research_agent import AnthropicAgent
from langchain_core.messages import HumanMessage


def update_task_status(
    task_id: str, 
    status: str, 
    report_path: str = None, 
    error: str = None
):
    """Helper to update task status with proper fields"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if status == "success":
                query = """
                    UPDATE tasks 
                    SET status = %s,
                        completed_at = NOW(),
                        report_path = %s,
                        error_message = NULL
                    WHERE task_id = %s
                """
                params = (status, report_path, task_id)
            else:
                query = """
                    UPDATE tasks 
                    SET status = %s,
                        completed_at = NOW(),
                        report_path = NULL,
                        error_message = %s
                    WHERE task_id = %s
                """
                params = (status, error, task_id)
                
            cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"Failed to update task status: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
        

@celery_app.task(bind=True, max_retries=3)
def generate_report_task(self, task_id: str, company_id: str):
    """
    Celery task to generate equity research report
    
    Args:
        task_id: Unique task identifier
        company_id: Company ID to generate report for
    """

    reports_dir = CONFIG["app"]["reports_path"]
    os.makedirs(reports_dir, exist_ok=True)
    try:
        response = asyncio.run(_execute_agent(company_id))
        
        # Save raw response to file
        raw_response_path = os.path.join(reports_dir, f"{task_id}_raw.txt")
        with open(raw_response_path, "w") as f:
            f.write(str(response))
            
        # Extract content from AIMessage
        report_content = response["messages"][-1].content if response.get("messages") else ""
        
        if not report_content:
            raise ValueError("Empty response from agent")
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save markdown report
        md_filename = f"{task_id}_{timestamp}.md"
        md_path = os.path.join(reports_dir, md_filename)
        with open(md_path, "w") as f:
            f.write(report_content)

        # Update task status to completed
        update_task_status(task_id, "success", report_path=md_path)
        # return {
        #     "status": "success",
        #     "task_id": task_id,
        #     "report_path": md_path
        # }
    except Exception as e:
        update_task_status(task_id, "failed", error=str(e))
        raise e

async def _execute_agent(company_id: str) -> dict:
    """Wrapper to run async agent workflow in Celery task"""
    agent = AnthropicAgent.initialize(CONFIG["anthropic"]["model"],CONFIG["anthropic"]["api_key"])
    executor = agent.build_executor()
    query = f"Generate report for company {company_id}"
    return await executor.ainvoke({"messages": [HumanMessage(content=query)]})