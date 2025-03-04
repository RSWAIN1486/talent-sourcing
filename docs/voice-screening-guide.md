# Voice Screening Guide

This document provides instructions for running the Voice Screening tests and using the Voice Screening functionality in the application.

## Table of Contents
- [Test Environment Setup](#test-environment-setup)
- [Running Voice Screening Tests](#running-voice-screening-tests)
  - [Using the Batch Script](#using-the-batch-script)
  - [Running Individual Tests](#running-individual-tests)
- [Running the Application](#running-the-application)
- [Using Voice Screening Features](#using-voice-screening-features)
- [Troubleshooting](#troubleshooting)

## Test Environment Setup

Before running tests, ensure you have:

1. Activated the correct conda environment for the backend
2. Installed all required dependencies with `pip install -r backend/requirements.txt`
3. Set up your environment variables in `.env` file in the backend directory, including:
   - Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
   - Ultravox API credentials
   - MongoDB connection string
   - Other necessary configurations

## Running Voice Screening Tests

### Using the Batch Script

The easiest way to run all Voice Screening tests is to use the provided batch script:

1. Navigate to the project root directory
2. Run the batch script:
   ```
   cd backend/tests/voice_screening
   run_tests.bat
   ```

This script will run all voice screening tests in the correct order:
- Unit tests (phone utilities, Ultravox API, voice screening service)
- Integration tests (voice call, voice screening, voice screening workflow)

### Running Individual Tests

You can also run individual test files as needed:

#### Unit Tests
Run from the backend directory:

```
# Phone utilities tests
pytest tests/voice_screening/test_phone_utils.py -v

# Ultravox API tests
pytest tests/voice_screening/test_ultravox.py -v

# Voice screening service tests
pytest tests/voice_screening/test_voice_screening_service.py -v
```

#### Integration Tests
Run from the backend directory:

```
# Voice call tests
python tests/voice_screening/test_voice_call.py

# Voice screening tests
python tests/voice_screening/test_voice_screening.py

# Voice screening workflow tests
python tests/voice_screening/test_voice_screening_workflow.py
```

## Running the Application

To run the backend application:

1. Navigate to the backend directory
2. Activate your conda environment
3. Run the application using uvicorn:
   ```
   cd backend
   uvicorn app.main:app --reload
   ```

The application will start on http://localhost:8000 by default.

## Using Voice Screening Features

The Voice Screening functionality allows you to:
- Screen candidates through automated phone calls
- Collect and analyze responses
- Review screening results

To use the Voice Screening features:
1. Log in to the application
2. Navigate to the Candidates section
3. Select a candidate to screen
4. Click on "Voice Screen" to initiate the voice screening process
5. Follow the prompts to configure and start the screening call
6. Access results in the candidate's profile after the call is completed

## Troubleshooting

Common issues and solutions:

### Test Failures
- Check if all environment variables are properly set
- Ensure Twilio and Ultravox credentials are valid
- Verify that your MongoDB connection is working

### Connection Issues
- Check your internet connection
- Verify that your Twilio account has sufficient credits
- Ensure the phone number format is correct

### Runtime Errors
- Check application logs for specific error messages
- Verify that all services (MongoDB, Twilio, Ultravox) are accessible
- Ensure all required dependencies are installed 