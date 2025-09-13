"""
Web search tool for the Vendor Background Check App.
Uses Google Custom Search API by default, with a fallback to a simpler search method.
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from config import settings
from src.utils.validation import validate_search_query, ValidationError
from src.utils.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int, time_frame: int):
        """
        Initialize the rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in the time frame
            time_frame: Time frame in seconds
        """
        self.max_calls = max_calls
        self.time_frame = time_frame
        self.calls: List[datetime] = []
        self.lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Acquire the rate limit lock."""
        await self.lock.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release the rate limit lock."""
        self.lock.release()
    
    async def wait_if_needed(self):
        """Wait if the rate limit has been reached."""
        now = datetime.now()
        
        # Remove old calls outside the time frame
        self.calls = [call for call in self.calls if now - call < timedelta(seconds=self.time_frame)]
        
        # If we've reached the limit, wait until the oldest call falls out of the time frame
        if len(self.calls) >= self.max_calls:
            oldest_call = self.calls[0]
            wait_time = (oldest_call - now + timedelta(seconds=self.time_frame)).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Add the current call
        self.calls.append(now)

class WebSearchTool:
    """Tool for performing web searches to gather information about vendors."""
    
    def __init__(self, api_key: Optional[str] = None, cse_id: Optional[str] = None):
        """Initialize the web search tool.
        
        Args:
            api_key: Google Custom Search API key
            cse_id: Google Custom Search Engine ID
        """
        # Use provided API keys or fallback to environment variables or None
        self.api_key = api_key or getattr(settings, 'GOOGLE_API_KEY', None)
        self.cse_id = cse_id or getattr(settings, 'GOOGLE_CSE_ID', None)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize rate limiter (100 queries per day for Google CSE free tier)
        self.rate_limiter = RateLimiter(max_calls=90, time_frame=24 * 60 * 60)  # 90 calls per 24 hours
        
    def _validate_search_params(self, query: str, num_results: int) -> None:
        """Validate search parameters.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Raises:
            ValidationError: If any parameter is invalid
        """
        try:
            validate_search_query(query)
        except ValidationError as e:
            raise ValidationError(f"Invalid search query: {str(e)}")
            
        if not isinstance(num_results, int) or num_results < 1 or num_results > 10:
            raise ValidationError("Number of results must be between 1 and 10")
    
    async def search_google_cse(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search using Google Custom Search API.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
            
        Returns:
            Dict containing search results or error information
            
        Raises:
            ValidationError: If search parameters are invalid
            requests.RequestException: If the API request fails
        """
        # Validate input parameters
        self._validate_search_params(query, num_results)
        
        if not self.api_key or not self.cse_id:
            raise ValueError("Google API key and CSE ID are required for this search method")
        
        try:
            async with self.rate_limiter:
                await self.rate_limiter.wait_if_needed()
                
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.api_key,
                    'cx': self.cse_id,
                    'q': query,
                    'num': num_results,
                    'safe': 'active'  # Enable safe search
                }
                
                # Add a small delay to avoid hitting rate limits too quickly
                await asyncio.sleep(0.5)
                
                response = requests.get(
                    url, 
                    params=params, 
                    timeout=10,
                    headers=self.headers
                )
                response.raise_for_status()
                
                results = response.json()
                
                # Log API usage
                search_info = results.get('searchInformation', {})
                logger.info(
                    f"Google CSE API: {search_info.get('totalResults', 0)} results "
                    f"found in {search_info.get('searchTime', 0)} seconds"
                )
                
                return {
                    'status': 'success',
                    'results': [
                        {
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        }
                        for item in results.get('items', [])
                    ]
                }
                
        except Exception as e:
            logger.error(f"Google CSE search failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web using available methods.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
            
        Returns:
            Dict containing search results
            
        Raises:
            ValidationError: If search parameters are invalid
            requests.RequestException: If the search request fails
        """
        # Validate input parameters
        self._validate_search_params(query, num_results)
        
        # Try Google CSE first if credentials are available
        if self.api_key and self.cse_id:
            try:
                return await self.search_google_cse(query, num_results)
            except Exception as e:
                logger.warning(f"Google CSE search failed, falling back to basic search: {str(e)}")
                # Continue to fallback method
        
        # Fallback to a simpler search method
        return await self._fallback_search(query, num_results)
    
    async def _fallback_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Fallback search method using a public search engine.
        
        Note: This is a simple implementation and may not work for all cases.
        In a production environment, you should use a proper search API.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
            
        Returns:
            Dict containing search results
            
        Raises:
            requests.RequestException: If the search request fails
        """
        try:
            # Add a delay to be respectful to the search engine
            await asyncio.sleep(1)
            
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = requests.get(
                search_url, 
                headers=self.headers, 
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results (this is a simplified example)
            for result in soup.select('.result__body') or soup.select('.result'):
                title_elem = result.select_one('h2 a') or result.select_one('.result__title a')
                link_elem = result.select_one('.result__url') or result.select_one('.result__url')
                snippet_elem = result.select_one('.result__snippet') or result.select_one('.result__snippet')
                
                if not all([title_elem, link_elem]):
                    continue
                
                # Clean and validate the URL
                link = link_elem.get('href', '').strip()
                if not link.startswith(('http://', 'https://')):
                    # Skip relative URLs or invalid links
                    continue
                    
                results.append({
                    'title': title_elem.get_text(strip=True)[:200],  # Limit title length
                    'link': link,
                    'snippet': (snippet_elem.get_text(strip=True) if snippet_elem else '')[:300]  # Limit snippet length
                })
                
                if len(results) >= num_results:
                    break
            
            logger.info(f"Fallback search returned {len(results)} results")
                    
            return {
                'status': 'success',
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Fallback search failed: {str(e)}"
            }
