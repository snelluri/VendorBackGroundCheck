"""
Public records search tool for the Vendor Background Check App.
Provides access to various public records data sources.
"""
import asyncio
import json
import random
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator

from config import settings
from src.utils.validation import (
    validate_business_name,
    validate_search_query,
    validate_email,
    validate_phone_number,
    ValidationError
)
from src.utils.logging_config import get_logger
from .web_search import RateLimiter  # Reuse the RateLimiter from web_search

# Initialize logger
logger = get_logger(__name__)

class PublicRecordsClient:
    """Client for accessing public records data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the public records client.
        
        Args:
            api_key: API key for the public records service
        """
        # Use provided API key or fallback to environment variable or None
        self.api_key = api_key or getattr(settings, 'PUBLIC_RECORDS_API_KEY', None)
        self.base_url = "https://api.publicrecords.example.com/v1"  # Example URL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize rate limiter (100 queries per day)
        self.rate_limiter = RateLimiter(max_calls=90, time_frame=24 * 60 * 60)  # 90 calls per 24 hours
        
        # Cache for storing recent queries to avoid duplicate API calls
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 3600  # Cache TTL in seconds (1 hour)
        self._last_cache_cleanup = time.time()
        
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request to the public records service.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters for the request
            
        Returns:
            JSON response from the API
            
        Raises:
            requests.RequestException: If the API request fails
        """
        # Add API key to parameters
        params['api_key'] = self.api_key
        
        # Make the request
        response = requests.get(
            f"https://api.publicrecords.example.com/{endpoint}",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()
        
    async def get_business_registration(self, business_name: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Get business registration information.
        
        Args:
            business_name: Name of the business to look up
            state: Optional state to narrow down the search
            
        Returns:
            Dictionary containing business registration details
        """
        try:
            # Validate and sanitize input
            business_name = validate_business_name(business_name)
            
            # Create cache key
            cache_key = f"business_registration:{business_name.lower()}:{state or 'all'}"
            
            # Check cache first
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
            
            # Apply rate limiting
            async with self.rate_limiter:
                await self.rate_limiter.wait_if_needed()
                
                # Simulate API delay
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # Generate mock data
                registration_date = datetime.now() - timedelta(days=random.randint(365, 3650))  # 1-10 years ago
                
                result = {
                    'status': 'success',
                    'business_name': business_name,
                    'registration_number': f"{'S' if state else 'F'}{random.randint(1000000, 9999999)}",
                    'registration_date': registration_date.strftime("%Y-%m-%d"),
                    'business_status': random.choice(['Active', 'Inactive', 'Good Standing', 'Delinquent']),
                    'jurisdiction': state or 'Federal',
                    'address': f"{random.randint(100, 9999)} {' '.join(random.choices(['Main', 'Oak', 'Pine', 'Maple', 'Cedar', 'Elm'], k=2))} St, {random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])} {random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'])} {random.randint(10000, 99999)}",
                    'officers': [
                        {
                            'name': f"{' '.join(random.choices(['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah'], k=2))} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}",
                            'title': random.choice(['CEO', 'President', 'Director', 'Secretary', 'Treasurer'])
                        }
                        for _ in range(random.randint(1, 3))
                    ]
                }
                
                # Cache the result
                self._set_to_cache(cache_key, result)
                return result
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Failed to retrieve business registration: {str(e)}",
                'details': str(e) if settings.DEBUG else None
            }
    
    async def get_legal_actions(self, business_name: str, 
                              jurisdiction: Optional[str] = None, 
                              years_back: int = 5) -> Dict[str, Any]:
        """Get legal actions involving the business.
        
        Args:
            business_name: Name of the business to look up
            jurisdiction: Optional jurisdiction to filter by (state/country)
            years_back: Number of years to look back for legal actions (max 10)
            
        Returns:
            Dictionary containing legal actions information
            
        Raises:
            ValidationError: If the input parameters are invalid
        """
        try:
            # Validate and sanitize input
            business_name = validate_business_name(business_name)
            if years_back < 1 or years_back > 10:
                raise ValidationError("years_back must be between 1 and 10")
                
            # Create cache key
            cache_key = f"legal_actions:{business_name.lower()}:{jurisdiction or 'all'}:{years_back}"
            
            # Check cache first
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
            
            # Apply rate limiting
            async with self.rate_limiter:
                await self.rate_limiter.wait_if_needed()
                
                # Simulate API call delay
                await asyncio.sleep(0.5)
                
                # Mock data - replace with actual API response
                result = {
                    'status': 'success',
                    'data': {
                        'business_name': business_name,
                        'jurisdiction': jurisdiction or 'Multiple',
                        'years_back': years_back,
                        'legal_actions': [
                            {
                                'case_number': f"CV-{random.randint(2020, 2023)}-{random.randint(1000, 9999)}",
                                'filing_date': '2022-03-10',
                                'case_type': 'Contract Dispute',
                                'status': 'Closed',
                                'outcome': 'Settled',
                                'plaintiff': 'ABC Supplier Co.',
                                'defendant': business_name,
                                'jurisdiction': jurisdiction or 'State Court',
                                'amount_in_dispute': f"${random.randint(10000, 1000000):,}"
                            }
                        ],
                        'summary': {
                            'total_cases': 1,
                            'open_cases': 0,
                            'closed_cases': 1,
                            'avg_case_duration_days': 120
                        }
                    },
                    'source': 'public_records_api',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Cache the result
                self._set_to_cache(cache_key, result)
                return result
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Failed to retrieve legal actions: {str(e)}",
                'details': str(e) if settings.DEBUG else None
            }
    
    async def get_licenses_and_permits(self, business_name: str, 
                                     license_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get licenses and permits for the business.
        
        Args:
            business_name: Name of the business to look up
            license_types: Optional list of license types to filter by
            
        Returns:
            Dictionary containing licenses and permits information
            
        Raises:
            ValidationError: If the input parameters are invalid
        """
        try:
            # Validate and sanitize input
            business_name = validate_business_name(business_name)
            
            # Create cache key
            cache_key = f"licenses:{business_name.lower()}"
            if license_types:
                cache_key += f":{':'.join(sorted(license_types))}"
                
            # Check cache first
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
            
            # Apply rate limiting
            async with self.rate_limiter:
                await self.rate_limiter.wait_if_needed()
                
                # Simulate API call delay
                await asyncio.sleep(0.5)
                
                # Mock data - replace with actual API response
                all_licenses = [
                    {
                        'license_type': 'Business License',
                        'license_number': f"BL-{random.randint(10000, 99999)}",
                        'issue_date': '2021-05-20',
                        'expiration_date': '2024-05-20',
                        'status': 'Active',
                        'issuing_authority': 'City of San Francisco',
                        'category': 'General Business'
                    },
                    {
                        'license_type': 'Sales Tax Permit',
                        'license_number': f"ST-{random.randint(100000, 999999)}",
                        'issue_date': '2021-06-15',
                        'expiration_date': '2025-06-15',
                        'status': 'Active',
                        'issuing_authority': 'California Department of Tax and Fee Administration',
                        'category': 'Tax'
                    },
                    {
                        'license_type': 'Health Department Permit',
                        'license_number': f"HD-{random.randint(1000, 9999)}",
                        'issue_date': '2022-01-10',
                        'expiration_date': '2023-12-31',
                        'status': 'Active',
                        'issuing_authority': 'County Health Department',
                        'category': 'Health & Safety'
                    }
                ]
                
                # Filter by license types if specified
                filtered_licenses = all_licenses
                if license_types:
                    filtered_licenses = [
                        lic for lic in all_licenses 
                        if any(lic_type.lower() in lic['license_type'].lower() 
                              for lic_type in license_types)
                    ]
                
                result = {
                    'status': 'success',
                    'data': {
                        'business_name': business_name,
                        'licenses': filtered_licenses,
                        'summary': {
                            'total_licenses': len(filtered_licenses),
                            'active_licenses': sum(1 for lic in filtered_licenses 
                                                 if lic.get('status') == 'Active'),
                            'expired_licenses': sum(1 for lic in filtered_licenses 
                                                  if lic.get('status') == 'Expired'),
                            'categories': list(set(lic.get('category', 'Other') 
                                                for lic in filtered_licenses))
                        }
                    },
                    'source': 'public_records_api',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Cache the result
                self._set_to_cache(cache_key, result)
                return result
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Failed to retrieve licenses and permits: {str(e)}",
                'details': str(e) if settings.DEBUG else None
            }
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached result."""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                del self._cache[cache_key]
        return None
    
    def _set_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache a result."""
        self._cache[cache_key] = (result, time.time())
        
        # Clean up cache periodically
        if time.time() - self._last_cache_cleanup > 3600:
            self._last_cache_cleanup = time.time()
            self._cache = {k: v for k, v in self._cache.items() if time.time() - v[1] < self._cache_ttl}
