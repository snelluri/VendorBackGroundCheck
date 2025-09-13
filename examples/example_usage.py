"""
Example usage of the Vendor Background Check application.

This script demonstrates how to use the application to perform a background check on a vendor.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agent.manager import BackgroundCheckManager
from src.tools.web_search import WebSearchTool
from src.tools.public_records import PublicRecordsClient

async def run_example():
    """Run an example background check."""
    print("=== Vendor Background Check Example ===\n")
    
    # Initialize components
    web_search = WebSearchTool()
    public_records = PublicRecordsClient()
    manager = BackgroundCheckManager()
    
    # Vendor to check
    vendor_name = "Acme Corporation"
    
    print(f"Starting background check for: {vendor_name}\n")
    
    # Example 1: Web Search
    print("1. Searching the web for information...")
    web_results = await web_search.search_web(f"{vendor_name} company profile")
    if web_results.get("status") == "success" and web_results.get("results"):
        print(f"   Found {len(web_results['results'])} search results.")
        for i, result in enumerate(web_results["results"][:3], 1):
            print(f"   {i}. {result['title']}")
        print()
    
    # Example 2: Public Records - Business Registration
    print("2. Checking business registration...")
    registration = await public_records.get_business_registration(vendor_name)
    if registration.get("status") == "success":
        print(f"   Business Name: {registration.get('business_name')}")
        print(f"   Registration #: {registration.get('registration_number')}")
        print(f"   Status: {registration.get('status')}")
        print(f"   Registration Date: {registration.get('registration_date')}")
        print()
    
    # Example 3: Public Records - Legal Actions
    print("3. Checking for legal actions...")
    legal_actions = await public_records.get_legal_actions(vendor_name)
    if legal_actions.get("status") == "success" and legal_actions.get("legal_actions"):
        print(f"   Found {len(legal_actions['legal_actions'])} legal actions.")
        for action in legal_actions["legal_actions"][:2]:  # Show first 2 actions
            print(f"   - {action['case_number']}: {action['case_type']} ({action['status']})")
    else:
        print("   No legal actions found.")
    print()
    
    # Example 4: Full background check using the agent
    print("4. Running full background check using AI agent...")
    result = await manager.process_request(vendor_name)
    print("\n=== Background Check Report ===")
    print(result["report"])
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_example())
