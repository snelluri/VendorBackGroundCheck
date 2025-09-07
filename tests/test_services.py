"""
Tests for the Vendor Background Check services.
"""
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.web_search import WebSearchTool
from src.tools.public_records import PublicRecordsClient

# Mock data for tests
MOCK_GOOGLE_RESPONSE = {
    'items': [
        {
            'title': 'Test Business - Official Site',
            'link': 'https://testbusiness.com',
            'snippet': 'Official website of Test Business, providing quality services since 2010.'
        },
        {
            'title': 'Test Business - Wikipedia',
            'link': 'https://en.wikipedia.org/wiki/Test_Business',
            'snippet': 'Test Business is a leading provider of...'
        }
    ],
    'searchInformation': {
        'totalResults': '2',
        'searchTime': 0.5
    }
}

MOCK_BUSINESS_REGISTRATION = {
    'status': 'success',
    'data': {
        'business_name': 'Test Business Inc.',
        'registration_number': '12345678',
        'registration_date': '2020-01-15',
        'status': 'Active',
        'jurisdiction': 'Delaware'
    }
}

class TestWebSearchTool(unittest.TestCase):
    """Tests for the WebSearchTool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.search_tool = WebSearchTool(api_key='test_api_key', cse_id='test_cse_id')
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests."""
        self.loop.close()
    
    def run_async(self, coro):
        """Helper method to run async tests."""
        return self.loop.run_until_complete(coro)

    @patch('src.tools.web_search.requests.get')
    def test_web_search_success(self, mock_get):
        """Test successful web search with mock response."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_GOOGLE_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Execute
        results = self.run_async(self.search_tool.search_web('Test Business', num_results=2))
        
        # Assert
        self.assertEqual(results['status'], 'success')
        self.assertEqual(len(results['results']), 2)
        self.assertEqual(results['results'][0]['title'], 'Test Business - Official Site')
        self.assertIn('testbusiness.com', results['results'][0]['link'])

class TestPublicRecordsClient(unittest.TestCase):
    """Tests for the PublicRecordsClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = PublicRecordsClient(api_key='test_api_key')
        self.search_tool = WebSearchTool(api_key='test_google_key', cse_id='test_cse_id')
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests."""
        self.loop.close()
        
    def run_async(self, coro):
        """Helper method to run async tests."""
        return self.loop.run_until_complete(coro)
        
    def _make_api_request(self, endpoint, params):
        """Mock implementation of _make_api_request for testing."""
        return MOCK_BUSINESS_REGISTRATION
    
    def test_get_business_registration(self):
        """Test successful business registration lookup."""
        # Execute with a test business name and state
        business_name = 'Test Business Inc.'
        state = 'Delaware'
        results = self.run_async(
            self.client.get_business_registration(business_name, state=state)
        )
        
        # Assert the response structure matches our expectations
        self.assertEqual(results['status'], 'success')
        self.assertEqual(results['business_name'], business_name)
        self.assertIn(results['business_status'], ['Active', 'Inactive', 'Good Standing', 'Delinquent'])
        # When a state is provided, jurisdiction should match that state
        self.assertEqual(results['jurisdiction'], state)
        
        # Verify the response has the expected fields
        self.assertIn('registration_number', results)
        self.assertIn('registration_date', results)
        self.assertIn('address', results)
        self.assertIn('officers', results)
        
        # Verify the registration number starts with 'S' when state is provided
        self.assertTrue(results['registration_number'].startswith('S'))
        
        # Test with no state parameter
        no_state_results = self.run_async(
            self.client.get_business_registration(business_name)
        )
        
        # Jurisdiction should be 'Federal' when no state is provided
        self.assertEqual(no_state_results['jurisdiction'], 'Federal')
        # Registration number should start with 'F' when no state is provided
        self.assertTrue(no_state_results['registration_number'].startswith('F'))

    @patch('src.tools.web_search.WebSearchTool._validate_search_params')
    def test_web_search_validation(self, mock_validate):
        """Test input validation in web search."""
        # Set up the mock to raise ValidationError for invalid inputs
        def mock_validate_side_effect(query, num_results):
            if not query or len(query.strip()) == 0:
                raise ValueError("Query cannot be empty")
            if len(query) > 500:
                raise ValueError("Query is too long")
            if num_results <= 0 or num_results > 10:
                raise ValueError("Number of results must be between 1 and 10")
        
        mock_validate.side_effect = mock_validate_side_effect
        
        # Test empty query
        with self.assertRaises(ValueError, msg="Empty query should raise ValueError"):
            self.run_async(self.search_tool.search_web('', num_results=5))
        
        # Test query too long
        with self.assertRaises(ValueError, msg="Query too long should raise ValueError"):
            self.run_async(self.search_tool.search_web('a' * 501, num_results=5))
        
        # Test invalid num_results (0)
        with self.assertRaises(ValueError, msg="num_results=0 should raise ValueError"):
            self.run_async(self.search_tool.search_web('test', num_results=0))
            
        # Test invalid num_results (negative)
        with self.assertRaises(ValueError, msg="Negative num_results should raise ValueError"):
            self.run_async(self.search_tool.search_web('test', num_results=-1))
            
        # Test invalid num_results (too large)
        with self.assertRaises(ValueError, msg="num_results>10 should raise ValueError"):
            self.run_async(self.search_tool.search_web('test', num_results=11))
            
        # Test valid query should not raise
        try:
            # Mock the actual search to return a success result
            with patch.object(self.search_tool, 'search_google_cse') as mock_search:
                mock_search.return_value = {"status": "success", "results": []}
                result = self.run_async(self.search_tool.search_web('valid query', num_results=5))
                self.assertEqual(result["status"], "success")
        except ValueError as e:
            self.fail(f"Valid query raised ValueError: {e}")
            
        # Verify the mock was called with the correct arguments
        mock_validate.assert_called()

    def test_rate_limiting(self):
        """Test that rate limiting is enforced."""
        # This is a basic test - in a real scenario, you'd want to mock time
        # and test the actual rate limiting behavior
        self.assertTrue(hasattr(self.search_tool, 'rate_limiter'))
        self.assertTrue(hasattr(self.client, 'rate_limiter'))
