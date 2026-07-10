import pytest
from scraper.utils import validate_url
from scraper.groww_scraper import GrowwScraper
from scraper.base_scraper import BaseScraper
import os

def test_validate_url():
    assert validate_url("https://groww.in") == True
    assert validate_url("not_a_url") == False

def test_base_scraper_instantiation():
    # BaseScraper is abstract, should raise TypeError
    with pytest.raises(TypeError):
        BaseScraper()

def test_groww_scraper_init():
    scraper = GrowwScraper("dummy_urls.json", "dummy_raw", "dummy_processed")
    assert scraper.urls_file == "dummy_urls.json"

def test_parse_html():
    scraper = GrowwScraper("dummy_urls.json", "dummy_raw", "dummy_processed")
    html_content = """
    <html>
        <body>
            <h1>Fund Name</h1>
            <table>
                <tr><td>Expense Ratio</td><td>0.5%</td></tr>
                <tr><td>Exit Load</td><td>1%</td></tr>
            </table>
            <p>Some more text here.</p>
        </body>
    </html>
    """
    scheme_meta = {"name": "Test Fund", "category": "Large Cap"}
    result = scraper.parse(html_content, "https://test.com", scheme_meta)
    
    assert "metadata" in result
    assert result["metadata"]["scheme_name"] == "Test Fund"
    assert "Expense Ratio" in result["fund_details"]
    assert result["fund_details"]["Expense Ratio"] == "0.5%"
    assert "Some more text here." in result["text"]
