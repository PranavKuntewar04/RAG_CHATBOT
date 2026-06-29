import os
import time
import logging
import urllib.robotparser
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scraper.urls import GROWW_URLS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = os.path.join("data", "raw")

def ensure_dirs():
    """Ensure raw data directory exists."""
    os.makedirs(RAW_DIR, exist_ok=True)

def setup_robot_parser(base_url: str):
    """Setup and return a robot parser for the given base URL."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{base_url}/robots.txt")
    try:
        rp.read()
    except Exception as e:
        logger.warning(f"Failed to read robots.txt from {base_url}: {e}")
    return rp

def extract_slug(url: str) -> str:
    """Extract slug from the url to be used as a filename."""
    return url.strip("/").split("/")[-1]

def fetch_with_retry(url: str, rp: urllib.robotparser.RobotFileParser, max_retries: int = 3) -> str:
    """Fetch URL with retry logic and rate limit delay."""
    parsed_url = urlparse(url)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MutualFundBot/1.0"
    
    if rp.site_maps() is not None or rp.mtime() != 0:
        if not rp.can_fetch(user_agent, url):
            logger.error(f"robots.txt disallows fetching {url}")
            return None

    headers = {"User-Agent": user_agent}

    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Simple check if page looks okay and not blocked by captcha
            if "captcha" in response.text.lower():
                 logger.warning("Captcha detected in response!")
            
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                sleep_time = settings.SCRAPE_DELAY_SECONDS * (attempt + 2)
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts.")
                return None
    return None

def scrape_single(url: str, rp: urllib.robotparser.RobotFileParser) -> dict:
    """Fetch one scheme page, return raw HTML + metadata and save to disk."""
    slug = extract_slug(url)
    html_content = fetch_with_retry(url, rp)
    
    if not html_content:
        return {"url": url, "status": "failed", "slug": slug}

    file_path = os.path.join(RAW_DIR, f"{slug}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    logger.info(f"Saved {slug}.html to {RAW_DIR}")
    return {"url": url, "status": "success", "slug": slug, "file_path": file_path}

def scrape_all() -> list[dict]:
    """Fetch each URL, parse HTML, return list of raw documents."""
    ensure_dirs()
    
    # We assume all URLs are from groww.in for robots.txt parsing
    base_url = "https://groww.in"
    logger.info(f"Setting up robots.txt for {base_url}")
    rp = setup_robot_parser(base_url)
    
    results = []
    for i, url in enumerate(GROWW_URLS):
        if i > 0:
            logger.info(f"Waiting for {settings.SCRAPE_DELAY_SECONDS} seconds before next request...")
            time.sleep(settings.SCRAPE_DELAY_SECONDS)
            
        result = scrape_single(url, rp)
        results.append(result)
        
    return results

if __name__ == "__main__":
    logger.info("Starting scraper...")
    results = scrape_all()
    
    success_count = sum(1 for r in results if r["status"] == "success")
    logger.info(f"Scraping completed. Successfully fetched {success_count}/{len(GROWW_URLS)} pages.")
