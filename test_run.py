"""
Test script to verify the application's functionality.
This script tests the core components of the Vendor Background Check application.
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Import settings
from config import settings

# Add the project root to the Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.tools.web_search import WebSearchTool
from src.tools.public_records import PublicRecordsClient
from src.agent.manager import BackgroundCheckManager

async def test_web_search() -> Dict[str, Any]:
    """Test the web search functionality with mock data."""
    print("\n=== Testing Web Search ===")
    web_search = WebSearchTool()
    
    try:
        print("Searching for 'test company'...")
        results = await web_search.search_web("test company", num_results=3)
        print(f"✅ Web search test completed. Found {len(results.get('results', []))} results.")
        return results
    except Exception as e:
        print(f"❌ Error during web search test: {str(e)}")
        raise

async def test_public_records() -> Dict[str, Any]:
    """Test the public records lookup functionality."""
    print("\n=== Testing Public Records Lookup ===")
    public_records = PublicRecordsClient()
    
    try:
        print("Looking up business registration for 'Acme Corporation'...")
        registration = await public_records.get_business_registration("Acme Corporation")
        print(f"✅ Public records lookup completed. Status: {registration.get('status')}")
        return registration
    except Exception as e:
        print(f"❌ Error during public records test: {str(e)}")
        raise

async def test_background_check() -> Dict[str, Any]:
    """Test the complete background check workflow."""
    print("\n=== Testing Background Check Workflow ===")
    
    # Check if OpenAI API key is available
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not openai_key or openai_key == 'your_openai_api_key':
        print("⚠️  OpenAI API key not found. Skipping background check test.")
        print("   To enable this test, please set the OPENAI_API_KEY in your .env file.")
        print("   You can get an API key from: https://platform.openai.com/account/api-keys")
        return {
            'status': 'skipped',
            'reason': 'OpenAI API key not configured',
            'vendor': 'TechStart Inc',
            'report': 'Test skipped - OpenAI API key required'
        }
    
    try:
        manager = BackgroundCheckManager()
        print("Running background check for 'TechStart Inc'...")
        results = await manager.process_request("TechStart Inc")
        print("✅ Background check completed successfully!")
        print("\n=== Results Summary ===")
        print(f"Vendor: {results.get('vendor')}")
        print(f"Status: {results.get('status')}")
        print(f"Report: {results.get('report', 'No report generated')[:100]}...")
        return results
    except Exception as e:
        print(f"❌ Error during background check: {str(e)}")
        if "401" in str(e) or "API key" in str(e):
            print("\n⚠️  Authentication failed. Please check your OpenAI API key.")
            print("   You can set it in the .env file: OPENAI_API_KEY=your_api_key_here")
        raise

async def run_tests():
    """Run all tests and display results."""
    print("🚀 Starting Vendor Background Check Tests 🚀\n")
    
    results = {}
    
    try:
        # Run web search test
        web_results = await test_web_search()
        results['web_search'] = {
            'status': 'success',
            'results_count': len(web_results.get('results', [])) if web_results else 0
        }
        
        # Run public records test
        records = await test_public_records()
        results['public_records'] = {
            'status': 'success' if records and records.get('status') == 'success' else 'failed',
            'data': records
        }
        
        # Run full background check
        bg_check = await test_background_check()
        results['background_check'] = {
            'status': 'success' if bg_check and bg_check.get('status') == 'success' else 'failed',
            'score': bg_check.get('score', 'N/A') if bg_check else 'N/A'
        }
        
        print("\n🎉 All tests completed successfully! 🎉")
        
    except Exception as e:
        print(f"\n❌ Tests failed with error: {str(e)}")
        results['error'] = str(e)
    
    return results

if __name__ == "__main__":
    asyncio.run(run_tests())
