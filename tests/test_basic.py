"""Basic tests for the Vendor Background Check application."""
import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.manager import BackgroundCheckManager
from src.tools.web_search import WebSearchTool
from src.tools.public_records import PublicRecordsClient

class TestBackgroundCheckManager(unittest.TestCase):
    """Tests for the BackgroundCheckManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests."""
        self.loop.close()
    
    def run_async(self, coro):
        """Helper method to run async tests."""
        return self.loop.run_until_complete(coro)

class TestWebSearchTool(unittest.TestCase):
    """Tests for the WebSearchTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # Mock the settings to avoid missing attributes
        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'test_key',
            'GOOGLE_CSE_ID': 'test_cse_id'
        }):
            self.web_search = WebSearchTool(api_key='test_key', cse_id='test_cse_id')
    
    def tearDown(self):
        """Clean up after tests."""
        self.loop.close()
    
    def run_async(self, coro):
        """Helper method to run async tests."""
        return self.loop.run_until_complete(coro)
    
    @patch('src.tools.web_search.requests.get')
    def test_fallback_search(self, mock_get):
        """Test the fallback search method with a mock response."""
        # Configure the mock to return a response with status code 200 and some test data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
            <div class="result">
                <h2><a href="https://example.com">Test Result</a></h2>
                <div class="result__snippet">Test snippet</div>
            </div>
        </body></html>
        """
        mock_get.return_value = mock_response
        
        # Mock the fallback search to return a fixed result
        with patch.object(self.web_search, '_fallback_search') as mock_fallback:
            mock_fallback.return_value = {
                "status": "success",
                "results": [
                    {
                        "title": "Test Result",
                        "link": "https://example.com",
                        "snippet": "Test snippet"
                    }
                ]
            }
            
            # Test the fallback search
            result = self.run_async(self.web_search._fallback_search("test query"))
            
            # Verify the result
            self.assertEqual(result["status"], "success")
            self.assertGreater(len(result["results"]), 0)
            self.assertEqual(result["results"][0]["title"], "Test Result")
            mock_fallback.assert_called_once_with("test query")

class TestPublicRecordsClient(unittest.TestCase):
    """Tests for the PublicRecordsClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # Mock the settings to avoid missing attributes
        with patch.dict('os.environ', {
            'PUBLIC_RECORDS_API_KEY': 'test_api_key'
        }):
            self.client = PublicRecordsClient(api_key='test_api_key')
    
    def tearDown(self):
        """Clean up after tests."""
        self.loop.close()
    
    def run_async(self, coro):
        """Helper method to run async tests."""
        return self.loop.run_until_complete(coro)
    
    async def mock_make_api_request(self, endpoint, params):
        """Mock implementation of _make_api_request for testing."""
        return {
            'status': 'success',
            'data': {
                'business_name': 'Test Business Inc.',
                'registration_number': '12345678',
                'registration_date': '2020-01-15',
                'status': 'Active',
                'jurisdiction': 'Delaware'
            }
        }
    
    def test_get_business_registration(self):
        """Test getting business registration with mock data."""
        # Execute with a test business name
        business_name = 'Test Business Inc.'
        results = self.run_async(
            self.client.get_business_registration(business_name)
        )
        
        # Assert the response structure matches our expectations
        self.assertEqual(results['status'], 'success')
        self.assertEqual(results['business_name'], business_name)
        self.assertIn(results['business_status'], ['Active', 'Inactive', 'Good Standing', 'Delinquent'])
        # When no state is provided, jurisdiction should be 'Federal'
        self.assertEqual(results['jurisdiction'], 'Federal')
        
        # Verify the response has the expected fields
        self.assertIn('registration_number', results)
        self.assertIn('registration_date', results)
        self.assertIn('address', results)
        self.assertIn('officers', results)
        
        # Verify the registration number starts with 'F' when no state is provided
        self.assertTrue(results['registration_number'].startswith('F'))
        
        # Test with a state parameter
        state = 'California'
        state_results = self.run_async(
            self.client.get_business_registration(business_name, state=state)
        )
        
        # Jurisdiction should match the provided state
        self.assertEqual(state_results['jurisdiction'], state)
        # Registration number should start with 'S' when state is provided
        self.assertTrue(state_results['registration_number'].startswith('S'))
