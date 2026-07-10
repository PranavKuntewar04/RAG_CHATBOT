from abc import ABC, abstractmethod
import requests
import os
import sys
import json

# Add scraper directory to path for direct-script execution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import rate_limiter, retry, validate_url

class BaseScraper(ABC):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    @retry(max_attempts=3, delay_seconds=2)
    @rate_limiter(min_seconds=1, max_seconds=3)
    def fetch(self, url: str) -> str:
        """Fetches raw HTML from a URL with retries and rate limiting."""
        if not validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
            
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        # If the page requires JS rendering, it might return a skeleton HTML.
        # We assume for now requests is enough, but we can extend to Selenium if needed.
        return response.text

    @abstractmethod
    def parse(self, html: str, url: str) -> dict:
        """Abstract method — subclasses implement parsing logic."""
        pass

    def save_raw(self, data: str, path: str):
        """Save raw HTML to file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)

    def save_processed(self, data: dict, path: str):
        """Save processed dictionary to JSON file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
