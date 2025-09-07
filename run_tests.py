#!/usr/bin/env python3
"""
Simple test runner for the Vendor Background Check application.
"""
import unittest
import sys

def run_tests():
    """Run all tests in the tests directory."""
    # Add the src directory to the path so we can import our modules
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if any tests failed
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    run_tests()
