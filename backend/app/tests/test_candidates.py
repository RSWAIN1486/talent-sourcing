import io
import pytest
from fastapi.testclient import TestClient
from bson import ObjectId

from app.main import app
from app.core.database import get_db
from app.models.database import Base
from app.models import schemas

def create_test_pdf():
    """Create a test PDF file in memory"""
    return io.BytesIO(b"Test PDF content")

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def job_id(client):
    """Create a job and return its ID for testing candidates"""
    response = client.post(
        "/api/v1/jobs/",
        json={
            "title": "Software Engineer",
            "description": "Test job",
            "responsibilities": "Test responsibilities",
            "requirements": "Test requirements"
        }
    )
    return response.json()["id"]

def test_upload_resume(client, job_id):
    # Create a test PDF file
    test_pdf = create_test_pdf()
    
    # Upload resume
    files = {
        "file": ("test.pdf", test_pdf, "application/pdf")
    }
    
    response = client.post(
        f"/api/v1/candidates/{job_id}/upload",
        files=files
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "resume_path" in data
    assert "id" in data
    assert data["job_id"] == job_id

def test_get_candidates(client, job_id):
    # First upload some resumes
    test_pdf = create_test_pdf()
    files = {
        "file": ("test.pdf", test_pdf, "application/pdf")
    }
    
    # Upload multiple resumes
    for _ in range(2):
        client.post(f"/api/v1/candidates/{job_id}/upload", files=files)
    
    # Get candidates for the job
    response = client.get(f"/api/v1/candidates/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(c["job_id"] == job_id for c in data)

def test_get_candidate(client, job_id):
    # First upload a resume
    test_pdf = create_test_pdf()
    files = {
        "file": ("test.pdf", test_pdf, "application/pdf")
    }
    
    response = client.post(f"/api/v1/candidates/{job_id}/upload", files=files)
    created_candidate = response.json()
    candidate_id = created_candidate["id"]
    
    # Get the candidate
    response = client.get(f"/api/v1/candidates/{job_id}/{candidate_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == candidate_id
    assert data["job_id"] == job_id

def test_get_nonexistent_candidate(client, job_id):
    nonexistent_id = str(ObjectId())
    response = client.get(f"/api/v1/candidates/{job_id}/{nonexistent_id}")
    assert response.status_code == 404