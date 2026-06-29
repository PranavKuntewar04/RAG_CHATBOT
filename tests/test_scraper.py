import pytest
import os
import tempfile
import urllib.robotparser
from unittest.mock import patch, mock_open
from src.scraper.groww_scraper import fetch_with_retry, extract_slug
from src.ingestion.parser import parse_html_file

def test_extract_slug():
    url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    assert extract_slug(url) == "hdfc-mid-cap-fund-direct-growth"

@patch("src.scraper.groww_scraper.requests.get")
def test_fetch_with_retry_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html>Test</html>"
    
    rp = urllib.robotparser.RobotFileParser()
    rp.can_fetch = lambda ua, url: True
    
    html = fetch_with_retry("http://test.com", rp)
    
    assert html == "<html>Test</html>"
    mock_get.assert_called_once()

def test_parse_html_file():
    html_content = """
    <html>
        <script id="__NEXT_DATA__">
            {"props": {"pageProps": {"mfServerSideData": {
                "scheme_name": "Test Fund",
                "nav": 100.5,
                "category": "Equity",
                "expense_ratio": 1.2
            }}}}
        </script>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html") as f:
        f.write(html_content)
        temp_path = f.name
        
    try:
        parsed_doc, slug = parse_html_file(temp_path)
        assert parsed_doc["scheme_name"] == "Test Fund"
        assert parsed_doc["structured_data"]["nav"] == "100.5"
        assert parsed_doc["structured_data"]["expense_ratio"] == "1.2%"
        assert "Equity" in parsed_doc["category"]
    finally:
        os.remove(temp_path)
