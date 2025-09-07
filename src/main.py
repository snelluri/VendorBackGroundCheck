"""
Vendor Background Check Application

This application performs background checks on vendors using AI and various data sources.
"""
import asyncio
import argparse
import logging
import os
from typing import Optional, Dict, Any
from pathlib import Path

# Import application components
from agent.manager import BackgroundCheckManager
from tools.web_search import WebSearchTool
from tools.public_records import PublicRecordsClient
from config.settings import settings
from utils import (
    configure_logging, 
    get_logger,
    validate_business_name,
    validate_search_query,
    ValidationError
)

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "vendor_check.log"

configure_logging(log_file=str(log_file.absolute()))
logger = get_logger(__name__)

class VendorBackgroundCheckApp:
    """Main application class for the Vendor Background Check system."""
    
    def __init__(self):
        """Initialize the application components."""
        # Initialize tools
        self.web_search = WebSearchTool()
        self.public_records = PublicRecordsClient()
        
        # Initialize the agent manager
        self.manager = BackgroundCheckManager()
        
        logger.info("Vendor Background Check application initialized")
    
    async def run_background_check(self, vendor_name: str) -> dict:
        """
        Run a background check on a vendor.
        
        Args:
            vendor_name: Name of the vendor to check
            
        Returns:
            Dictionary containing the background check results
            
        Raises:
            ValidationError: If the vendor name is invalid
        """
        try:
            # Validate and sanitize the vendor name
            vendor_name = validate_business_name(vendor_name)
            logger.info(f"Starting background check for vendor: {vendor_name}")
            
            # Validate the search query
            search_query = f"{vendor_name} company profile"
            validate_search_query(search_query)
            # Run the background check using the agent manager
            result = await self.manager.process_request(vendor_name)
            
            logger.info(f"Completed background check for {vendor_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error during background check for {vendor_name}: {str(e)}")
            return {
                'vendor': vendor_name,
                'status': 'error',
                'error': str(e)
            }

async def main():
    """Main entry point for the application."""
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Vendor Background Check Tool')
    parser.add_argument('vendor', nargs='?', help='Name of the vendor to check')
    parser.add_argument('--output', '-o', help='Output file for the report (JSON format)')
    args = parser.parse_args()
    
    # Initialize the application
    app = VendorBackgroundCheckApp()
    
    # Get vendor name from command line or prompt
    vendor_name = args.vendor
    if not vendor_name:
        vendor_name = input("Enter vendor name to check: ")
    
    try:
        # Validate the vendor name before proceeding
        vendor_name = validate_business_name(vendor_name)
    except ValidationError as e:
        logger.error(f"Invalid vendor name: {str(e)}")
        print(f"Error: {str(e)}. Please provide a valid business name.")
        return
    
    # Run the background check
    result = await app.run_background_check(vendor_name)
    
    # Output the results
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Report saved to {args.output}")
    else:
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(result)

if __name__ == "__main__":
    asyncio.run(main())
