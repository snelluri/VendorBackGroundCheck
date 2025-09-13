# Vendor Background Check - Testing Guide

This document provides step-by-step instructions for setting up and testing the Vendor Background Check application locally.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- Required API keys (see Configuration section)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd vendor-background-check
```

### 2. Create and Activate Virtual Environment

#### On macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   ```bash
   # Application Settings
   DEBUG=True
   CACHE_ENABLED=True
   RATE_LIMIT_PER_MINUTE=60
   
   # Note: For testing without external API keys, the application uses mock data
   # To test with real services, you'll need to provide the appropriate API keys:
   # OPENAI_API_KEY=your_openai_api_key
   # GOOGLE_CSE_ID=your_google_cse_id
   # GOOGLE_API_KEY=your_google_api_key
   # PUBLIC_RECORDS_API_KEY=your_public_records_api_key
   ```

## Running Tests

### Unit Tests

The test suite is designed to work without external API keys by using mock data.

Run all unit tests:
```bash
pytest tests/
```

Run a specific test file:
```bash
pytest tests/test_services.py -v
```

### Testing with Mock Data

When running without API keys, the application will use mock data for:
- Web search results
- Public records lookups
- Any other external API calls

To verify the mock data is being used, look for log messages indicating "Using mock data" in the test output.

### Running the Example

Run the example script to test the application:
```bash
python -m examples.example_usage
```

## Manual Testing

### 1. Start the Python REPL

```bash
python
```

### 2. Import and Run the Background Check

```python
import asyncio
from examples.example_usage import run_example

# Run the example
asyncio.run(run_example())
```

## Testing Different Scenarios

1. **Basic Vendor Search**
   - Test with a well-known company name
   - Test with a local business
   - Test with an international company

2. **Error Cases**
   - Test with an empty company name
   - Test with special characters
   - Test with very long company names

3. **Rate Limiting**
   - Test the rate limiting by making multiple rapid requests

## Verifying Results

1. Check the console output for search results and public records information
2. Verify that the application handles errors gracefully
3. Check the logs (if any) for detailed information

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure all required API keys are set in the `.env` file
   - Verify the keys have the correct permissions

2. **Dependency Issues**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.8+)

3. **Rate Limiting**
   - If you hit rate limits, wait for the rate limit window to reset
   - Consider increasing rate limits in your API provider's dashboard

## Cleanup

When done testing, deactivate the virtual environment:
```bash
deactivate
```

## Additional Resources

- [API Documentation](#) (Add link to your API documentation if available)
- [Troubleshooting Guide](#) (Add link to detailed troubleshooting if available)
