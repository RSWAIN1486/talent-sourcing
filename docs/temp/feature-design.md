# Deployment and Docker Configuration

## Docker Setup
The application has been containerized using Docker with a multi-container setup using docker-compose. This setup includes:

1. Frontend Container (Next.js):
   - Base image: node:18-alpine
   - Exposed port: 3000
   - Environment variables:
     - NEXT_PUBLIC_API_URL: Points to backend service

2. Backend Container (FastAPI):
   - Base image: python:3.9-slim
   - Exposed port: 8000
   - Environment variables:
     - CORS_ORIGINS: Allowed origins for CORS
     - DEEP_INFRA_API_TOKEN: API token for Deep Infra

## Deployment Options

### Recommended Platforms (Cost-Effective):

1. Railway.app
   - Free tier available
   - Supports Docker deployments
   - Easy GitHub integration
   - Good for full-stack applications

2. DigitalOcean
   - Basic droplet from $4/month
   - Full infrastructure control
   - Native Docker support

3. Render
   - Free tier available
   - Docker support
   - Simple deployment process

4. Fly.io
   - Generous free tier
   - Global deployment
   - Docker-native platform

## Local Development with Docker

To run the application locally using Docker:

1. Create a `.env` file with required environment variables
2. Build and start containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## Production Deployment Steps

1. Choose a deployment platform
2. Set up environment variables
3. Configure CI/CD pipeline if needed
4. Deploy Docker containers
5. Set up monitoring and logging 

## Deployment Alternatives Analysis

### Replit Evaluation
- Provides automatic HTTPS with subdomain (your-app.repl.co)
- No manual SSL certificate management needed
- No known HTTPS/HTTP routing issues
- Limitations:
  - Cold starts on free tier
  - Memory limitations (500MB-2GB)
  - Requires keeping repl "alive"
  - Potential reliability concerns

### AWS Alternative
- Most flexible and scalable
- Services to consider:
  - AWS Elastic Beanstalk
  - AWS EC2 + RDS
  - AWS Amplify
- Benefits:
  - Complete infrastructure control
  - Robust security features
  - Extensive free tier
  - No routing issues

### GCP Alternative
- Similar to AWS capabilities
- Services to consider:
  - Google App Engine
  - Google Cloud Run
  - Google Compute Engine
- Benefits:
  - Strong performance
  - Good documentation
  - Free tier available
  - Built-in security features

### Recommendation
Based on the application requirements and the HTTPS routing issues faced with Render:

1. If seeking a quick solution: Try Replit first as it handles HTTPS automatically
2. For production-grade deployment: 
   - AWS Elastic Beanstalk or Google App Engine for managed services
   - AWS EC2 or Google Compute Engine for full control 

# Voice Agent Integration for Recruitment AI

## Overview
This document outlines the integration of a Voice Agent system into the Recruitment AI application to enable automated phone screening of candidates. This feature will allow recruiters to initiate AI-powered phone calls to candidates directly from the application.

## Requirements

1. Enable recruiters to initiate an AI-powered call to candidates from the job details page
2. AI should greet the candidate and conduct a 3-5 minute screening interview
3. AI should collect key information:
   - Confirm candidate's interest in job opportunities
   - Current notice period
   - Current and expected compensation
   - Ask relevant technical questions based on the job description
4. After the call, the system should:
   - Save the call transcript 
   - Generate a screening score
   - Update the candidate's record with the collected information
   - Update job statistics (screened candidate count)

## Technical Design

### Backend Changes

1. New Endpoints:
   - `/api/v1/candidates/{job_id}/candidates/{candidate_id}/voice-screen`: Initiate a voice screening call
   - `/api/v1/candidates/callback/call-complete`: Webhook for receiving call results 

2. Voice Agent Integration:
   - Integration with Ultravox AI API for voice synthesis
   - Integration with Twilio for phone call functionality
   - System to generate appropriate screening questions based on job description

3. Data Model Changes:
   - Add fields to Candidate model:
     - `call_transcript`: Text transcript of the screening call
     - `screening_score`: Numerical score based on the call
     - `notice_period`: Candidate's notice period
     - `current_compensation`: Current salary/compensation
     - `expected_compensation`: Expected salary/compensation
     - `screening_in_progress`: Boolean flag to indicate an ongoing call

### Third-Party Integration Details

#### Twilio Integration
1. **Authentication**:
   - `TWILIO_ACCOUNT_SID`: Twilio account identifier
   - `TWILIO_AUTH_TOKEN`: Authentication token for API access
   - `TWILIO_PHONE_NUMBER`: Purchased phone number to make outbound calls

2. **API Calls**:
   - Initialize Twilio client with credentials
   - Create outbound call using `calls.create()` method
   - Configure webhook URL for call status events
   - Handle callbacks for call completion events

3. **Webhook Handling**:
   - Receive call status updates via webhook
   - Parse Twilio webhook data format (CallSid, CallStatus, etc.)
   - Update database with call results

#### Ultravox AI Integration
1. **Authentication**:
   - `ULTRAVOX_API_KEY`: API key for authentication
   - `ULTRAVOX_API_BASE_URL`: Base URL for the Ultravox API

2. **API Calls**:
   - Create voice agent with job-specific prompt
   - Configure agent voice and parameters
   - Link agent to Twilio call
   - Retrieve call transcript and analysis

3. **Data Flow**:
   - System prompt based on job description
   - Voice agent handles the conversation
   - Transcript and analysis retrieved after call completion
   - Results parsed and stored in candidate record

### Webhook Configuration
1. **Public URL Requirement**:
   - Webhook requires a publicly accessible URL
   - Use ngrok for local development
   - Use deployment URL in production

2. **Webhook URL Format**:
   - `{WEBHOOK_BASE_URL}{API_V1_STR}/candidates/callback/call-complete`
   - Must be configured in environment variables

3. **Security Considerations**:
   - No authentication for webhook (Twilio limitation)
   - Validate incoming webhook data
   - Rate limiting to prevent abuse

### Frontend Changes

1. UI Updates:
   - Update the Call button functionality in the JobDetails page
   - Add loading state during call initiation
   - Add notification for call completion
   - Add tooltips to display screening information

2. State Management:
   - Update candidate data after call completion
   - Refresh job statistics
   - Handle loading states during API calls

## Implementation Plan

1. Backend:
   - Set up required environment variables for Twilio and Ultravox
   - Implement voice screening API endpoints
   - Develop AI prompt engineering for screening questions
   - Implement callback handling for call results
   - Add phone number formatting utility

2. Frontend:
   - Update Call button implementation
   - Add status indicators for call progress
   - Implement tooltips for screening results

3. Testing:
   - Unit tests for phone number formatting
   - Unit tests for voice screening service
   - Integration tests for API endpoints
   - End-to-end testing with real credentials

## Security Considerations

1. Phone number validation before initiating calls
2. Secure storage of call transcripts
3. Proper authentication for API endpoints
4. Compliance with telecommunication regulations
5. Proper error handling for API failures
6. Rate limiting for call initiations

## Future Enhancements

1. Call scheduling for future times
2. Custom question templates per job
3. Multi-language support for international candidates
4. Call recording options
5. Retry mechanism for failed calls
6. Custom voice selection for different job roles
7. Monitoring dashboard for active calls
8. Advanced analytics on call performance and candidate responses 