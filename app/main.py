# app/main.py
from fastapi import FastAPI,HTTPException,status
import toml
import uuid
from datetime import datetime
from app.database import get_db_connection
from app.models import TaskCreate, TaskStatus
from app.tasks import generate_report_task
from app.data_loader import data_loader

config = toml.load("config.toml")

app = FastAPI(title="Equity Research Report API")

# Helper function to validate company ID (placeholder)
def validate_company_id(company_id: str) -> bool:
    """Check if company exists in metadata."""
    return data_loader.validate_company(company_id)

@app.post("/tasks", response_model=TaskStatus, status_code=status.HTTP_202_ACCEPTED)
async def create_task(task: TaskCreate):
    """
    Endpoint to submit a new report generation task
    
    Parameters:
    - company_id: Target company ID from provided dataset
    
    Returns:
    - Task metadata with initial status
    """
    if not validate_company_id(task.company_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid company ID. Check company_metadata.json"
        )

    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Create database record
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks 
                (task_id, company_id, status)
                VALUES (%s, %s, %s)
                """,
                (task_id, task.company_id, "pending")
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()

    # Trigger Celery task
    generate_report_task.delay(task_id, task.company_id)

    return {
        "task_id": task_id,
        "company_id": task.company_id,
        "status": "pending",
        "created_at": datetime.now(),
        "completed_at": None,
        "report_path": None
    }


@app.get("/tasks", response_model=list[TaskStatus])
async def list_tasks():
    """
    Retrieve all report generation tasks
    
    Returns:
    - List of tasks ordered by creation time
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM tasks 
                ORDER BY created_at DESC
                """
            )
            results = cursor.fetchall()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()
    
    return results

@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """
    Get details for a specific task
    
    Parameters:
    - task_id: UUID of the task
    
    Returns:
    - Full task metadata including final report path
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM tasks 
                WHERE task_id = %s
                """,
                (task_id,)
            )
            result = cursor.fetchone()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()
    
    if not result:
        raise HTTPException(404, "Task not found")
    
    return result

@app.post("/reports/{company_id}")
async def create_report(company_id: str):
    """
    For Users to submit a generation task for a particular company.
    """
    # Validate company_id format
    if not company_id or len(company_id) > 20:
        raise HTTPException(status_code=400, detail="Invalid company ID")
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Store task in database
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (task_id, company_id, status) VALUES (%s, %s, %s)",
                (task_id, company_id, "pending")
            )
        conn.commit()
    finally:
        conn.close()
    
    # Start async task
    task = generate_report_task.delay(company_id)
    return {"task_id": task_id, "status": "pending"}

@app.get("/reports/status/{task_id}")
async def get_report_status(task_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
            task = cursor.fetchone()
            
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        return {
            "task_id": task["task_id"],
            "company_id": task["company_id"],
            "status": task["status"],
            "created_at": task["created_at"],
            "completed_at": task["completed_at"]
        }
    finally:
        conn.close()

@app.get("/reports/{task_id}")
async def get_report(task_id: str):
    """
    For User to view their previously generated reports.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
            task = cursor.fetchone()
            
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        if task["status"] != "success":
            raise HTTPException(status_code=400, detail=f"Report not ready. Current status: {task['status']}")

        # In a real implementation, you would return the actual report
        # This could be a file download or JSON data
        return {
            "task_id": task["task_id"],
            "company_id": task["company_id"],
            "report_path": task["report_path"],
            "completed_at": task["completed_at"]
        }
    finally:
        conn.close()