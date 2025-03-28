# app/main.py
from fastapi import FastAPI,HTTPException,status, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.jwt_auth import create_access_token, get_current_user
import markdown
import uuid
import os
from datetime import datetime, timedelta
from app.database import get_db_connection
from app.models import TaskCreate, TaskStatus, Token
from app.tasks import generate_report_task
from app.data_loader import data_loader
from app.auth import verify_api_key, get_current_user_from_token_or_api_key
from config.config_load import CONFIG

app = FastAPI(title="Equity Research Report API")

# Helper function to validate company ID (placeholder)
def validate_company_id(company_id: str) -> bool:
    """Check if company exists in metadata."""
    return data_loader.validate_company(company_id)

@app.post("/tasks", response_model=TaskStatus, status_code=status.HTTP_202_ACCEPTED)
async def create_task(task: TaskCreate, user: dict = Depends(get_current_user_from_token_or_api_key)):
    """
    Endpoint to submit a new report generation task
    
    Parameters:
    - company_id: Target company ID from provided dataset
    
    Returns:
    - Task metadata with initial status
    """
    if not task.company_id.isdigit():
        raise HTTPException(400, "company_id must be a numeric string")
    
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
                (task_id, company_id, status, user_id)
                VALUES (%s, %s, %s, %s)
                """,
                (task_id, task.company_id, "pending", user["user_id"])
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
async def list_tasks(user: dict = Depends(get_current_user_from_token_or_api_key)):
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
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user["user_id"],)
            )
            results = cursor.fetchall()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()
    
    return results

@app.get("/tasks/{task_id}", response_model=TaskStatus, dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str, user: dict = Depends(get_current_user_from_token_or_api_key)):
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
                WHERE task_id = %s AND user_id = %s
                """,
                (task_id, user["user_id"])
            )
            result = cursor.fetchone()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()
    
    if not result:
        raise HTTPException(404, "Task not found")
    
    return result

@app.get("/reports/{task_id}/view", response_class=HTMLResponse)
async def view_report(task_id: str, user: dict = Depends(get_current_user_from_token_or_api_key)):
    """
    View the generated report in HTML format
    
    Parameters:
    - task_id: UUID of the task
    
    Returns:
    - HTML page with the report content
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT report_path, status FROM tasks 
                WHERE task_id = %s AND user_id = %s
                """,
                (task_id, user["user_id"])
            )
            result = cursor.fetchone()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()
    
    if not result:
        raise HTTPException(404, "Task not found")
    
    report_path, status = result.get("report_path"), result.get("status")
    
    if status != "success":
        raise HTTPException(400, f"Report not ready. Current status: {status}")
    
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(404, "Report file not found")
    
    # Read markdown content
    with open(report_path, 'r') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Add styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Equity Research Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #333366; }}
            h2 {{ color: #333366; border-bottom: 1px solid #cccccc; padding-bottom: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .download-link {{ display: inline-block; margin-top: 20px; padding: 10px 15px;
                           background-color: #4CAF50; color: white; text-decoration: none;
                           border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            {html_content}
            <a href="/reports/{task_id}" class="download-link">Download PDF</a>
        </div>
    </body>
    </html>
    """
    return styled_html

@app.get("/reports/{task_id}", dependencies=[Depends(verify_api_key)])
async def download_report(task_id: str, user: dict = Depends(verify_api_key)):
    """
    Download the generated report for a specific task
    
    Parameters:
    - task_id: UUID of the task
    
    Returns:
    - PDF file download
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT report_path, status FROM tasks 
                WHERE task_id = %s AND user_id = %s
                """,
                (task_id, user["user_id"])
            )
            result = cursor.fetchone()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()
    
    if not result:
        raise HTTPException(404, "Task not found")
    
    report_path, status = result.get("report_path"), result.get("status")
    
    if status != "success":
        raise HTTPException(400, f"Report not ready. Current status: {status}")
    
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(404, "Report file not found")
    
    return FileResponse(
        path=report_path,
        filename=os.path.basename(report_path),
        # media_type="application/pdf"
        media_type="text/markdown"
    )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint
    
    This endpoint allows users to obtain a JWT token by providing
    username and password. For simplicity, we accept any username
    with the password from config.
    
    Args:
        form_data: OAuth2 form with username and password
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # For simplicity, use a fixed password from config
    # In a real application, you would verify against a database
    valid_password = CONFIG["app"].get("DEFAULT_PASSWORD", "password")
    
    if form_data.password != valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with user information
    access_token_expires = timedelta(minutes=40)
    access_token = create_access_token(
        data={"sub": form_data.username, "username": form_data.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}