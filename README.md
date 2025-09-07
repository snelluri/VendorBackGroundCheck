# Vendor Background Check App

An AI-powered application for conducting comprehensive background checks on vendors using agentic AI frameworks. This application helps organizations verify vendor information, check business registrations, and analyze vendor reliability.

## ✨ Features

- **Web Search Integration**: Search for vendor information across the web
- **Public Records Lookup**: Access business registration and legal records
- **AI-Powered Analysis**: Intelligent analysis of vendor information
- **Rate Limiting**: Built-in rate limiting for API calls
- **Caching**: Performance optimization through response caching
- **Extensible Architecture**: Easy to add new data sources and analysis modules
- **Secure**: Environment-based configuration for sensitive data

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- API keys for required services (Google CSE, Public Records API, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vendor-background-check.git
   cd vendor-background-check
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your API keys and configuration.

## 🛠 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# API Keys
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
PUBLIC_RECORDS_API_KEY=your_public_records_api_key

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CACHE_TTL=3600  # Cache time-to-live in seconds
RATE_LIMIT=50   # Max API calls per minute
```

## 📖 User Guide

### Basic Usage

1. **Import the necessary modules**
   ```python
   from src.tools.web_search import WebSearchTool
   from src.tools.public_records import PublicRecordsClient
   ```

2. **Initialize the tools**
   ```python
   # Web search tool
   web_search = WebSearchTool()
   
   # Public records client
   public_records = PublicRecordsClient()
   ```

3. **Search for vendor information**
   ```python
   # Web search
   search_results = await web_search.search("Acme Corporation")
   
   # Business registration lookup
   business_info = await public_records.get_business_registration("Acme Corporation", state="California")
   ```

### Example: Complete Vendor Check

```python
import asyncio
from src.tools.web_search import WebSearchTool
from src.tools.public_records import PublicRecordsClient

async def check_vendor(vendor_name: str, state: str = None):
    """Run a complete background check on a vendor."""
    web_search = WebSearchTool()
    public_records = PublicRecordsClient()
    
    print(f"🔍 Running background check on {vendor_name}...")
    
    # Web search
    print("\n🌐 Searching the web...")
    web_results = await web_search.search(vendor_name)
    
    # Business registration
    print("\n🏢 Checking business registration...")
    registration = await public_records.get_business_registration(vendor_name, state=state)
    
    # Legal actions (if any)
    print("\n⚖️ Checking for legal actions...")
    legal_actions = await public_records.get_legal_actions(vendor_name, jurisdiction=state)
    
    return {
        'web_search': web_results,
        'registration': registration,
        'legal_actions': legal_actions
    }

# Run the check
if __name__ == "__main__":
    results = asyncio.run(check_vendor("Acme Corporation", "California"))
    print("\n✅ Background check complete!")
```

## 🚀 Deployment

### Local Development

1. **Run the application**
   ```bash
   python -m src.main
   ```

2. **Run tests**
   ```bash
   python -m pytest tests/
   ```

### Production Deployment

1. **Install production dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up a production WSGI server** (example using Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 src.wsgi:app
   ```

3. **Set up environment variables**
   Ensure all required environment variables are set in your production environment.

4. **Configure a reverse proxy** (example with Nginx)
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure all required API keys are set in your `.env` file
   - Verify the keys have the correct permissions

2. **Rate Limiting**
   - The application has built-in rate limiting
   - Check the logs for rate limit messages
   - Consider upgrading your API plan if you hit limits frequently

3. **Connection Issues**
   - Verify your internet connection
   - Check if the API services are up and running

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python 3.8+
- Uses various open-source libraries (see `requirements.txt`)
- Inspired by the need for better vendor due diligence tools
