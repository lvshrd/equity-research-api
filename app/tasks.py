# app/tasks.py
from app.celery_config import celery
from app.database import get_db_connection
from datetime import datetime
import os
from app.llm_service import AnthropicService
from app.data_loader import data_loader
import httpx

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

@celery.task(bind=True, max_retries=3)
def generate_report_task(self, task_id: str, company_id: str):
    """
    Celery task to generate research report
    
    Args:
        task_id: Unique identifier for tracking
        company_id: Target company ID
    """
    # Get company data
    try:
        company_data = data_loader.get_company_data(company_id)
    except ValueError as e:
        update_task_status(task_id, "failed", str(e))
        return

    # Generate report
    llm = AnthropicService()
    prompt = llm.build_prompt(company_data)
    try:
        # For async compatibility in Celery
        report_content = httpx.post(llm.base_url).json()  # Sync call for demo
        # In production use async version with proper await
        
        report_content=str(report_content)
        if not report_content:
            raise ValueError("Empty response from LLM")
            
        # Save report
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_filename = f"{task_id}_{company_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        report_path = os.path.join(report_dir, report_filename)
        with open(report_path, "w") as f:
            f.write(report_content)
            
        # Update database
        update_task_status(task_id, "success",report_path=report_path)
    except Exception as e:
        update_task_status(task_id, "failed", str(e))
        self.retry(exc=e, countdown=60)
