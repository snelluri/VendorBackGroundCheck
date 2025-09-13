# Vendor Background Check - User Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Running Background Checks](#running-background-checks)
4. [Understanding the Output](#understanding-the-output)
5. [Troubleshooting](#troubleshooting)
6. [Frequently Asked Questions](#frequently-asked-questions)

## Quick Start

1. **Install the package**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Run a background check**
   ```python
   from src.agent.manager import BackgroundCheckManager
   
   async def run_check():
       manager = BackgroundCheckManager()
       result = await manager.process_request("Acme Corporation")
       print(result['report'])
   
   import asyncio
   asyncio.run(run_check())
   ```

## Configuration

### Required Settings
- `OPENAI_API_KEY`: Your OpenAI API key for AI analysis

### Optional Settings
- `GOOGLE_API_KEY` & `GOOGLE_CSE_ID`: For enhanced web searches
- `PUBLIC_RECORDS_API_KEY`: For official business records lookup
- `DEBUG`: Set to `True` for detailed logs
- `CACHE_ENABLED`: Enable/disable response caching
- `RATE_LIMIT_PER_MINUTE`: API call rate limit

## Running Background Checks

### Basic Usage
```python
from src.agent.manager import BackgroundCheckManager

async def check_vendor(vendor_name):
    manager = BackgroundCheckManager()
    try:
        result = await manager.process_request(vendor_name)
        print(f"Status: {result['status']}")
        print(f"Report: {result['report']}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Run the check
import asyncio
asyncio.run(check_vendor("Example Corp"))
```

### Using the Command Line
```bash
python -m src.main --vendor "Acme Corporation"
```

### Example Script
See `examples/example_usage.py` for a complete working example.

## Understanding the Output

The background check returns a dictionary with:
- `vendor`: The vendor name that was checked
- `status`: Check status (e.g., "completed", "failed")
- `report`: Detailed findings in markdown format
- `timestamp`: When the check was performed
- `sources`: List of data sources used

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: Missing required API key
   ```
   **Solution**: Add your API key to the `.env` file

2. **Rate Limit Exceeded**
   ```
   Error: Rate limit exceeded
   ```
   **Solution**: Wait or increase your rate limit

3. **No Results Found**
   **Solution**: Try a more specific search term or verify the vendor name

### Getting Help

1. Check the logs for detailed error messages
2. Run with `DEBUG=True` for more information
3. Open an issue on GitHub with:
   - Steps to reproduce
   - Error message
   - Environment details

## Frequently Asked Questions

### Q: Can I use this without any API keys?
A: Yes, but with limited functionality. The app will use mock data when API keys are not provided.

### Q: How accurate are the results?
A: Results depend on the quality of available data. Always verify critical information through official channels.

### Q: Is my data stored anywhere?
A: By default, results are only stored in memory. API responses may be cached based on your configuration.

### Q: How can I customize the report format?
A: You can modify the prompt templates in the `src/agent/prompts/` directory.

## Support

For additional help, please contact [Your Support Email] or open an issue in our GitHub repository.
