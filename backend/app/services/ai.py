import PyPDF2
from typing import Dict, Any
import re
from openai import OpenAI
from pathlib import Path
import json
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client with environment variables
openai = OpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_BASE_URL,
)


async def analyze_resume(file_path: str) -> Dict[str, Any]:
    """
    Analyze a resume using the Llama model.
    """
    # Extract text from PDF
    text = extract_text_from_pdf(file_path)
    
    # Analyze resume using Llama
    analysis = await analyze_text_with_llama(text)
    
    return {
        "skills": analysis["skills"],
        "score": analysis["score"]
    }

async def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file.
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""
    return text

async def analyze_text_with_llama(text: str) -> Dict[str, Any]:
    """
    Analyze resume text using the Llama model.
    """
    # Prepare the prompt for skills extraction
    skills_prompt = f"""
    You are an AI resume analyzer. Extract technical skills from the following resume text and rate each skill's proficiency level from 0.0 to 1.0 based on the context and experience described. Only include skills that are clearly demonstrated in the text.

    Resume text:
    {text}

    Provide your response in the following format:
    {{"python": 0.8, "javascript": 0.7}}
    Only include the JSON object, nothing else.
    """

    # Get skills with confidence scores
    skills_response = openai.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": skills_prompt}],
    )
    skills_text = skills_response.choices[0].message.content.strip()
    
    # Clean up the response to ensure it's valid JSON
    skills_text = re.sub(r'[^{}:,."0-9a-zA-Z_-]', '', skills_text)
    skills = eval(skills_text)  # Using eval since we trust the input (it's from our AI)

    # Prepare the prompt for overall score
    score_prompt = f"""
    You are an AI resume analyzer. Based on the following resume text, provide a single overall score from 0.0 to 1.0 that represents the candidate's qualifications. Consider factors like:
    - Relevant experience
    - Education
    - Technical skills
    - Project complexity
    - Career progression

    Resume text:
    {text}

    Provide only the numerical score (e.g., 0.85), nothing else.
    """

    # Get overall score
    score_response = openai.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": score_prompt}],
    )
    score = float(score_response.choices[0].message.content.strip())

    return {
        "skills": skills,
        "score": score
    }

async def extract_resume_info(file_path: str) -> Dict[str, Any]:
    """Extract basic information from resume using LLM"""
    text = await extract_text_from_pdf(file_path)
    
    # Prepare the prompt for information extraction
    info_prompt = f"""
    You are an AI resume analyzer. Extract the following information from the resume text:
    - Full Name
    - Email Address
    - Phone Number
    - Location (City, State/Country)

    Resume text:
    {text}

    Provide your response in the following JSON format:
    {{
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-234-567-8900",
        "location": "San Francisco, CA"
    }}
    Only include the JSON object, nothing else. If a field is not found, use null.
    """

    # Get basic information
    info_response = openai.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": info_prompt}],
    )
    info_text = info_response.choices[0].message.content.strip()
    
    # Clean up the response and parse JSON
    info_text = re.sub(r'```json\s*|\s*```', '', info_text)  # Remove code blocks if present
    try:
        info = json.loads(info_text)
    except json.JSONDecodeError:
        # Fallback to empty values if JSON parsing fails
        info = {
            "name": "",
            "email": "",
            "phone": None,
            "location": None
        }
    
    return info

async def analyze_resume(file_path: str) -> Dict[str, Any]:
    """Analyze resume content and compute score using LLM"""
    text = await extract_text_from_pdf(file_path)
    
    # Prepare the prompt for skills extraction
    skills_prompt = f"""
    You are an AI resume analyzer. Extract technical skills from the following resume text and rate each skill's proficiency level from 0.0 to 1.0 based on the context and experience described. Consider:
    - Years of experience with the skill
    - Projects using the skill
    - Level of responsibility
    - Certifications or training
    - Recent usage of the skill

    Resume text:
    {text}

    Provide your response in the following JSON format:
    {{
        "skills": {{"python": 0.8, "javascript": 0.7}},
        "score": 0.85
    }}
    The score should be an overall assessment from 0.0 to 1.0 based on:
    - Relevant experience
    - Education
    - Technical skills
    - Project complexity
    - Career progression

    Only include the JSON object, nothing else.
    """

    # Get skills and score
    analysis_response = openai.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": skills_prompt}],
    )
    analysis_text = analysis_response.choices[0].message.content.strip()
    
    # Clean up the response and parse JSON
    analysis_text = re.sub(r'```json\s*|\s*```', '', analysis_text)  # Remove code blocks if present
    try:
        result = json.loads(analysis_text)
        # Convert score to 0-100 scale
        result["score"] = result["score"] * 100
    except json.JSONDecodeError:
        # Fallback to empty values if JSON parsing fails
        result = {
            "skills": {},
            "score": 0.0
        }
    
    return result 

async def analyze_call_transcript(summary: str) -> Dict[str, Any]:
    """
    Analyze a voice screening summary using OpenAI to extract structured data.
    
    Args:
        summary: The screening summary from Ultravox
        
    Returns:
        Dict containing analysis results including:
        - screening_score: Overall score (0-100)
        - notice_period: Standardized notice period
        - current_compensation: Standardized current compensation
        - expected_compensation: Standardized expected compensation
    """
    if not summary or summary == "No summary available":
        logger.warning("No valid summary provided for analysis")
        return {
            "screening_score": 0,
            "notice_period": "Not specified",
            "current_compensation": "Not specified",
            "expected_compensation": "Not specified"
        }
    
    analysis_prompt = f"""
    You are an AI recruitment assistant analyzing a voice screening summary.
    
    Summary:
    {summary}
     Please analyze this transcript and extract the following information:
    
    1. Notice period: Extract the candidate's notice period and standardize it to a clear format (e.g., "30 days", "2 months", "immediate"). If not mentioned, use "Unknown".
    
    2. Current compensation: Extract the candidate's current compensation and standardize it (e.g., "$90,000/year", "₹25 lakhs per annum"). If not mentioned, use "Unknown".
    
    3. Expected compensation: Extract the candidate's expected compensation and standardize it. If not mentioned, use "Unknown".
    
    4. Screening score: Provide a score from 0 to 100 based on how well the candidate communicated, their qualifications, and overall fit for the role.
 
    
    Provide your response in the following JSON format:
    {{
        "notice_period": "standardized period",
        "current_compensation": "standardized amount",
        "expected_compensation": "standardized amount",
        "screening_score": numeric_score
    }}
    Only include the JSON object, nothing else.
    """
    
    try:
        # Use the same model as other AI functions
        analysis_response = openai.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",  # Same model as resume analysis
            messages=[{"role": "user", "content": analysis_prompt}],
        )
        analysis_text = analysis_response.choices[0].message.content.strip()
        
        # Clean up and parse the response
        analysis_text = re.sub(r'```json\s*|\s*```', '', analysis_text)
        result = json.loads(analysis_text)
        
        # Ensure screening_score is an integer
        if "screening_score" in result:
            result["screening_score"] = int(float(result["screening_score"]))
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing call summary with OpenAI: {str(e)}")
        return {
            "screening_score": 0,
            "notice_period": "Not specified",
            "current_compensation": "Not specified",
            "expected_compensation": "Not specified"
        } 