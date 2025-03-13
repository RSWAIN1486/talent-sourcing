# Project Memory

## Environment Information
- Backend conda environment: 'ts'

## Import Error Fixes

1. **Missing Module Errors**: When encountering a `ModuleNotFoundError` or `ImportError`, check:
   - If the module exists in the expected location
   - If the function being imported exists in the specified module
   - If there's a circular import issue

2. **Specific Fixes Applied**:
   - Created `app.core.security` module to re-export `get_current_user` from `app.api.deps`
   - Added `get_candidate_by_id` function to `app.models.database` that was being imported by `voice_screening.py`
   - Created `app.core.logging` module to provide a standardized logging interface

This document records important learnings and insights gained during the development process to prevent repeating mistakes and to preserve knowledge for future reference.

## Voice Agent Integration

### Key Learnings

1. **API Integration**: Voice Agent integration requires multiple services working together:
   - Ultravox API for voice synthesis and conversation
   - Twilio API for phone call functionality
   - Our own backend for coordination and data management

2. **Asynchronous Processing**: We need to account for asynchronous processing when handling call results:
   - Calls may take several minutes to complete
   - Results need to be processed via webhook
   - UI needs to handle async state changes

3. **Environment Variables**: Multiple environment variables are required for integration:
   - Twilio account credentials (SID, auth token, phone number)
   - Ultravox API keys
   - Webhook URLs

4. **Phone Number Formatting**: Be mindful of international phone number formatting:
   - Use E.164 format for Twilio (+country code)
   - Validate phone numbers before initiating calls
   - Handle different regional formats appropriately

5. **Webhook Requirements**: Webhooks require a publicly accessible URL:
   - Local development requires a tunnel like ngrok
   - Domain verification may be required for some services
   - Always use HTTPS for security
   - URL must remain stable during a call's lifecycle

6. **API Error Handling**: Robust error handling is essential for external API calls:
   - Set appropriate timeouts
   - Implement retry mechanisms for transient failures
   - Gracefully handle service outages
   - Update UI to reflect error states
   - Provide fallbacks where possible

7. **Testing Techniques**: Effective testing requires mocking external services:
   - Use dependency injection to make services mockable
   - Create detailed mock responses that match real API responses
   - Test both success and error paths
   - Use integration tests to validate endpoint behavior
   - Separate unit tests from API-dependent tests for faster runs

8. **Test Suite Maintenance**: Ensuring tests remain in sync with implementation:
   - Always update tests when modifying function signatures
   - Make sure all tested functions actually exist in the implementation
   - Organize tests by feature and use descriptive file naming
   - Use fixtures to avoid code duplication in tests
   - Add comprehensive error messages to test scripts for easier debugging

9. **HTTP Client Libraries**: Different HTTP client libraries have different APIs:
   - `aiohttp` uses context managers with `async with session.post() as response:`
   - `httpx` has a more direct API: `response = await client.post()`
   - Response properties may differ (`status` vs `status_code`, etc.)
   - Ensure your tests and mocks match the library being used

10. **Async Testing Mocks**: Mocking async methods requires special consideration:
    - For methods that are awaited (like `response.json()`), define the mock as an async function
    - Using `AsyncMock(return_value=x)` doesn't work correctly for awaited methods
    - Instead, define async functions that return the desired values: `async def mock_json(): return {"key": "value"}`
    - Set these async functions as the mock method: `mock_response.json = mock_json`
    - This ensures the mock returns an awaitable that resolves to the expected value

11. **Mocking HTTP Clients Properly**: When mocking HTTP clients in async tests, be careful with the approach:
    - Avoid using `AsyncMock` for methods that aren't awaited (like `raise_for_status()`)
    - Use `MagicMock` with regular function definitions for synchronous methods
    - Use async functions for methods that return coroutines that need to be awaited
    - When patching, target the specific method rather than the entire client to avoid hierarchy issues
    - Example of proper mocking for httpx:
      ```python
      async def mock_post(*args, **kwargs):
          mock_response = MagicMock()
          # Use regular method for synchronous functions
          def mock_raise_for_status():
              return None
          mock_response.raise_for_status = mock_raise_for_status
          
          # Use async function for methods that return coroutines
          async def mock_json():
              return {"id": "test_id"}
          mock_response.json = mock_json
          return mock_response
      
      # Patch the specific method
      with patch('httpx.AsyncClient.post', mock_post):
          result = await client.post_something()
      ```

### Potential Challenges

1. **Call Flow Management**: Managing the conversation flow requires careful prompt engineering:
   - Ensuring the AI covers all required topics
   - Handling unexpected responses
   - Limiting call duration appropriately

2. **Error Handling**: Multiple points of failure need proper error handling:
   - API connectivity issues
   - Invalid phone numbers
   - Call drops or rejections
   - Webhook delivery failures

3. **Service Reliability**: External service downtime can impact application functionality:
   - Implement circuit breakers for repeated failures
   - Create fallback mechanisms where possible
   - Add monitoring and alerting for service health
   - Implement graceful degradation when services are unavailable

4. **Cost Management**: Voice calls and AI services have usage-based pricing:
   - Implement rate limiting to prevent abuse
   - Track usage metrics for budgeting
   - Consider batch processing for efficiency
   - Optimize prompts to reduce token usage

5. **Data Security**: Call recordings and transcripts contain sensitive information:
   - Implement proper data retention policies
   - Encrypt sensitive information
   - Follow regulations regarding call recording consent
   - Ensure data is properly anonymized for analysis

6. **Test-Implementation Synchronization**: Tests can fall out of sync with implementation:
   - Always check that tested functions and classes exist before running tests
   - Add thorough docstrings to help future developers understand test requirements
   - Follow a "test-first" approach when adding new features
   - Update tests immediately when changing function signatures

7. **Async Mocking Gotchas**: Async mocking can be tricky to get right:
   - Watch for "coroutine was never awaited" warnings in tests
   - Ensure test assertions run after all awaitable operations complete
   - AsyncMock may not work as expected for methods that are directly awaited
   - If a method in your production code has changed from sync to async or vice versa, tests will likely break

## Voice Agent Configuration System

We've implemented a comprehensive voice agent configuration system that allows for both global settings and job-specific customizations:

### Backend Components

1. **Models**:
   - `GlobalVoiceConfig`: Stores system-wide voice agent settings
   - `JobVoiceConfig`: Stores job-specific voice agent settings
   - `VoiceModel`: Enum for available voice models
   - `VoiceLanguage`: Enum for supported languages
   - `VoiceInfo`: Information about available voices

2. **Services**:
   - `voice_agent.py`: Handles CRUD operations for voice agent configurations
   - Integration with Ultravox API for fetching available models and voices
   - MongoDB storage for configuration persistence

3. **API Endpoints**:
   - Global configuration management
   - Job-specific configuration management
   - Available voices and models retrieval

### Frontend Components

1. **API Services**:
   - Voice agent configuration API client
   - Type definitions for voice agent configurations

2. **UI Components**:
   - Global voice settings page in user profile
   - Job-specific voice settings in job details
   - Voice model and voice selection interfaces
   - Temperature and other parameter controls

3. **User Experience**:
   - Intuitive interface for configuring voice agents
   - Preview capabilities for testing voices
   - Job-specific overrides for customization

### Integration Points

1. **Candidate Screening**:
   - Voice agent configurations are applied during candidate screening
   - Job-specific settings override global settings when specified
   - System prompts and questions are customizable

2. **Profile Management**:
   - User profile includes voice agent configuration
   - Global settings accessible from profile page
   - Account information displayed alongside settings

This implementation provides a flexible and user-friendly way to customize the voice agent's behavior both globally and per job, enhancing the screening experience for both recruiters and candidates. 