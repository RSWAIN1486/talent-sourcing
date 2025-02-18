import os
import pytest
import asyncio
from datetime import datetime
from fastapi import UploadFile
from io import BytesIO
from PyPDF2 import PdfWriter, PdfReader
from app.services.candidates import upload_resume, process_pdf_file
from app.services.ai import extract_resume_info, analyze_resume
from app.models.database import User

# Mock user for testing
TEST_USER = User(**{
    "_id": "507f1f77bcf86cd799439011",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": True,
    "is_superuser": False,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
})

# Test job ID
TEST_JOB_ID = "507f1f77bcf86cd799439012"

@pytest.mark.asyncio
async def test_pdf_extraction(test_pdf_path):
    """Test PDF text extraction"""
    info = await extract_resume_info(test_pdf_path)
    print("\nExtracted Information:")
    print(f"Name: {info.get('name')}")
    print(f"Email: {info.get('email')}")
    print(f"Phone: {info.get('phone')}")
    print(f"Location: {info.get('location')}")
    
    assert isinstance(info, dict)
    assert 'name' in info
    assert 'email' in info
    assert 'phone' in info
    assert 'location' in info

@pytest.mark.asyncio
async def test_resume_analysis(test_pdf_path):
    """Test resume analysis and scoring"""
    analysis = await analyze_resume(test_pdf_path)
    print("\nResume Analysis:")
    print(f"Score: {analysis.get('score')}")
    print("Skills:")
    for skill, score in analysis.get('skills', {}).items():
        print(f"- {skill}: {score}")
    
    assert isinstance(analysis, dict)
    assert 'skills' in analysis
    assert 'score' in analysis
    assert isinstance(analysis['skills'], dict)
    assert isinstance(analysis['score'], (int, float))
    assert 0 <= analysis['score'] <= 100

@pytest.mark.asyncio
async def test_process_pdf(test_pdf_path, test_db):
    """Test complete PDF processing"""
    result = await process_pdf_file(test_pdf_path, TEST_JOB_ID, TEST_USER)
    print("\nProcessed Result:")
    print(f"Candidate ID: {result['id']}")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Score: {result['resume_score']}")
    print("Skills:", result['skills'])
    
    assert result['id'] is not None
    assert isinstance(result['id'], str)
    assert result['job_id'] == TEST_JOB_ID
    assert result['resume_score'] >= 0
    assert isinstance(result['skills'], dict)

@pytest.mark.asyncio
async def test_upload_resume(test_pdf_path, test_db):
    """Test resume upload endpoint"""
    # Create UploadFile object
    with open(test_pdf_path, 'rb') as f:
        content = f.read()
    
    # Create a BytesIO object with the content
    file_like = BytesIO(content)
    file_like.name = "test_resume.pdf"
    
    file = UploadFile(
        filename="test_resume.pdf",
        file=file_like
    )
    
    result = await upload_resume(TEST_JOB_ID, file, TEST_USER)
    print("\nUpload Result:")
    print(f"Candidate ID: {result['id']}")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Score: {result['resume_score']}")
    print("Skills:", result['skills'])
    
    assert result['id'] is not None
    assert isinstance(result['id'], str)
    assert result['job_id'] == TEST_JOB_ID
    assert result['resume_score'] >= 0
    assert isinstance(result['skills'], dict)

@pytest.fixture
def test_pdf_path():
    """Create a test PDF file"""
    pdf_content = """
    John Doe
    Software Engineer
    john.doe@example.com
    +1 (123) 456-7890
    San Francisco, CA

    Experience:
    - Senior Software Engineer at Tech Corp (2018-present)
      * Led development of Python microservices
      * Implemented React frontend applications
      * Managed AWS cloud infrastructure
    
    Skills:
    - Python, JavaScript, React, AWS
    - Docker, Kubernetes, CI/CD
    - Agile methodologies
    
    Education:
    - BS Computer Science, Stanford University
    """
    
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)
    pdf_path = os.path.join(test_dir, "test_resume.pdf")
    
    # Create a PDF using PyPDF2
    pdf_writer = PdfWriter()
    page = pdf_writer.add_blank_page(width=612, height=792)  # Letter size
    page.insert_text(
        text=pdf_content,
        x=72,
        y=720,
        font_size=12,
        font_name="Helvetica"
    )
    
    with open(pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    
    yield pdf_path
    
    # Cleanup
    os.remove(pdf_path)
    os.rmdir(test_dir)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 