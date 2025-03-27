# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from config import CONFIG

# Load config for API key
API_KEY = CONFIG["app"]["API_KEY"]

client = TestClient(app)

def test_create_task_without_api_key():
    """Test creating task without API key should fail"""
    response = client.post("/tasks", json={"company_id": "42601"})
    assert response.status_code == 401

def test_create_task_with_api_key():
    """Test creating task with valid API key"""
    response = client.post(
        "/tasks", 
        json={"company_id": "42601"},
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

def test_get_task_details():
    """Test getting task details"""
    # First create a task
    response = client.post(
        "/tasks", 
        json={"company_id": "42601"},
        headers={"X-API-Key": API_KEY}
    )
    task_id = response.json()["task_id"]
    
    # Then get its details
    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id

def test_list_tasks():
    """Test listing all tasks"""
    response = client.get(
        "/tasks",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)