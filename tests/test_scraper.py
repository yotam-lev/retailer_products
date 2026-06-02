import pytest
import json
from unittest.mock import patch, MagicMock
from src.scraper import scrape_and_parse

# Test cases for Scraper
def test_scrape_and_parse_valid_json():
    with patch('src.scraper.sync_playwright') as mock_pw, \
         patch('src.scraper.requests.post') as mock_post:
        
        # Setup mock playwright
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.inner_text.return_value = "Valid content"
        
        # Setup mock ollama response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"product_name": "Hay", "price": 10.0, "quantity": 1.0, "measurement": "bale"}'}
        mock_post.return_value = mock_response
        
        result = scrape_and_parse("http://test.com")
        assert result["product_name"] == "Hay"
        assert result["price"] == 10.0

def test_scrape_and_parse_furniture_exclusion():
    with patch('src.scraper.sync_playwright') as mock_pw, \
         patch('src.scraper.requests.post') as mock_post:
        
        mock_page = MagicMock()
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value = mock_page
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"error": "physical_bed"}'}
        mock_post.return_value = mock_response
        
        result = scrape_and_parse("http://test.com")
        assert result == {"error": "physical_bed"}

def test_scrape_and_parse_malformed_json():
    with patch('src.scraper.sync_playwright') as mock_pw, \
         patch('src.scraper.requests.post') as mock_post:
        
        mock_page = MagicMock()
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value = mock_page
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Some random text with no json"}
        mock_post.return_value = mock_response
        
        result = scrape_and_parse("http://test.com")
        assert result is None

def test_scrape_and_parse_playwright_timeout():
    with patch('src.scraper.sync_playwright') as mock_pw:
        mock_browser = MagicMock()
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value.goto.side_effect = Exception("Timeout")
        
        result = scrape_and_parse("http://test.com")
        assert result is None
