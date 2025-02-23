from fastapi.testclient import TestClient
import pytest
from bson import ObjectId
from datetime import datetime

from app.main import app
from app.core.mongodb import get_database

@pytest.fixture
def client():
    yield TestClient(app)

@pytest.fixture
async def test_job():
    """Create a test job"""
    job_data = {
        "_id": ObjectId(),
        "title": "Test Job",
        "description": "Test Description",
        "responsibilities": "Test Responsibilities",
        "requirements": "Test Requirements",
        "total_candidates": 0,
        "resume_screened": 0,
        "phone_screened": 0,
        "created_by_id": ObjectId(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db = await get_database()
    await db.jobs.insert_one(job_data)
    yield job_data
    await db.jobs.delete_one({"_id": job_data["_id"]})

def test_create_job(client):
    response = client.post(
        "/api/v1/jobs/",
        json={
            "title": "Software Engineer",
            "description": "We are looking for a software engineer",
            "responsibilities": "Develop and maintain software applications",
            "requirements": "Python, FastAPI, MongoDB"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Software Engineer"
    assert "id" in data

def test_read_job(client):
    # First create a job
    job_data = {
        "title": "Software Engineer",
        "description": "We are looking for a software engineer",
        "responsibilities": "Develop and maintain software applications",
        "requirements": "Python, FastAPI, MongoDB"
    }
    response = client.post("/api/v1/jobs/", json=job_data)
    created_job = response.json()
    job_id = created_job["id"]

    # Then read it
    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["description"] == job_data["description"]

def test_read_nonexistent_job(client):
    nonexistent_id = str(ObjectId())
    response = client.get(f"/api/v1/jobs/{nonexistent_id}")
    assert response.status_code == 404

def test_update_job(client):
    # First create a job
    job_data = {
        "title": "Software Engineer",
        "description": "We are looking for a software engineer",
        "responsibilities": "Develop and maintain software applications",
        "requirements": "Python, FastAPI, MongoDB"
    }
    response = client.post("/api/v1/jobs/", json=job_data)
    created_job = response.json()
    job_id = created_job["id"]

    # Then update it
    updated_data = {
        "title": "Senior Software Engineer",
        "description": "We are looking for a senior software engineer",
        "responsibilities": "Lead and develop software applications",
        "requirements": "Python, FastAPI, MongoDB, Leadership"
    }
    response = client.put(f"/api/v1/jobs/{job_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == updated_data["title"]
    assert data["description"] == updated_data["description"]

def test_delete_job(client):
    # First create a job
    job_data = {
        "title": "Software Engineer",
        "description": "We are looking for a software engineer",
        "responsibilities": "Develop and maintain software applications",
        "requirements": "Python, FastAPI, MongoDB"
    }
    response = client.post("/api/v1/jobs/", json=job_data)
    created_job = response.json()
    job_id = created_job["id"]

    # Then delete it
    response = client.delete(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200

    # Verify it's deleted
    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 404

def test_list_jobs(client):
    # Create multiple jobs
    job_data = [
        {
            "title": "Software Engineer",
            "description": "Description 1",
            "responsibilities": "Responsibilities 1",
            "requirements": "Requirements 1"
        },
        {
            "title": "Data Scientist",
            "description": "Description 2",
            "responsibilities": "Responsibilities 2",
            "requirements": "Requirements 2"
        }
    ]
    
    for job in job_data:
        client.post("/api/v1/jobs/", json=job)
    
    response = client.get("/api/v1/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == job_data[0]["title"]
    assert data[1]["title"] == job_data[1]["title"] 