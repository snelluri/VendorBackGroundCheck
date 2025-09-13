# Vendor Background Check - Setup Guide

This guide will help you set up the Vendor Background Check application on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vendor-background-check
   ```

2. **Create and activate a virtual environment** (recommended)
   
   ### On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   ### On Windows:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your API keys if you have them:
   ```
   # Required for full functionality
   OPENAI_API_KEY=your_openai_api_key
   
   # Optional: For enhanced web search capabilities
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   
   # Optional: For public records access
   PUBLIC_RECORDS_API_KEY=your_public_records_api_key
   
   # Application settings
   DEBUG=True
   CACHE_ENABLED=True
   RATE_LIMIT_PER_MINUTE=60
   ```

## Running the Application

### Run the example script
```bash
python -m examples.example_usage
```

### Run tests
```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_services.py -v

# Run the comprehensive test script
python test_run.py
```

## Testing Without API Keys

The application includes mock data for testing basic functionality without API keys. When API keys are not provided:
- Web searches will return mock results
- Public records lookups will use simulated data
- Background checks will be limited to local data processing

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Errors**
   - Ensure your API keys are correctly set in the `.env` file
   - Verify the keys have the necessary permissions
   - Check for rate limits or quota restrictions

3. **Python Version**
   Make sure you're using Python 3.8 or higher:
   ```bash
   python --version
   ```

## Getting Help

If you encounter any issues or have questions, please check the following:
- [Documentation](docs/) for detailed usage instructions
- [Issue Tracker](<repository-url>/issues) for known issues
- Contact the development team for support

## License

Include your license information here.
