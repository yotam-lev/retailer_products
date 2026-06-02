import sys
import os
import subprocess
from unittest.mock import patch, MagicMock

# Import the function from src/scraper
sys.path.append('/Users/Yotam/Documents/terrapura/retailer_products/src')
from scraper import scrape_and_parse

# Test 1: Handle FileNotFoundError
with patch('subprocess.run', side_effect=FileNotFoundError("No such file or directory: 'ollama'")):
    print("Testing FileNotFoundError...")
    result = scrape_and_parse("https://example.com")
    print(f"Result for FileNotFoundError: {result}")

# Test 2: Handle CalledProcessError
with patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd='ollama')):
    print("\nTesting CalledProcessError...")
    result = scrape_and_parse("https://example.com")
    print(f"Result for CalledProcessError: {result}")

