from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re
from .base_scraper import BaseScraper

class GrowwScraper(BaseScraper):
    def __init__(self, urls_file: str, raw_dir: str, processed_dir: str):
        super().__init__()
        self.urls_file = urls_file
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

    def extract_fund_details(self, soup, tables):
        """Parse expense ratio, exit load, NAV, AUM, benchmark, etc."""
        fund_details = {}
        # Simple heuristic: Look for known keys in all extracted tables
        keys_to_find = ['Expense Ratio', 'Exit Load', 'NAV', 'AUM', 'Benchmark', 'Fund Size']
        
        for table in tables:
            for k, v in table.items():
                for target_key in keys_to_find:
                    if target_key.lower() in k.lower():
                        fund_details[target_key] = v
                        
        return fund_details

    def extract_sip_details(self, soup, tables):
        """Parse min SIP amount, SIP dates, SIP frequency"""
        sip_details = {}
        keys_to_find = ['Min. SIP Amount', 'Minimum SIP', 'SIP Dates', 'SIP']
        
        for table in tables:
            for k, v in table.items():
                for target_key in keys_to_find:
                    if target_key.lower() in k.lower():
                        sip_details[target_key] = v
                        
        return sip_details

    def extract_risk_info(self, soup, tables):
        """Parse riskometer classification, category"""
        risk_info = {}
        keys_to_find = ['Risk', 'Riskometer', 'Category']
        
        for table in tables:
            for k, v in table.items():
                for target_key in keys_to_find:
                    if target_key.lower() in k.lower():
                        risk_info[target_key] = v
        return risk_info

    def parse(self, html: str, url: str, scheme_meta: dict) -> dict:
        """Extract scheme-specific sections from Groww HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # HTML Stripping
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg', 'button']):
            tag.decompose()
            
        # Table Extraction
        tables_data = []
        for table in soup.find_all(['table', 'div']): # Groww sometimes uses divs for tables
            table_dict = {}
            
            # Real tables
            if table.name == 'table':
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) == 2:
                        key = cols[0].get_text(strip=True)
                        val = cols[1].get_text(strip=True)
                        if key and val:
                            table_dict[key] = val
                            
            if table_dict:
                tables_data.append(table_dict)
                
        # Also extract structured sections
        fund_details = self.extract_fund_details(soup, tables_data)
        sip_details = self.extract_sip_details(soup, tables_data)
        risk_info = self.extract_risk_info(soup, tables_data)

        # Text Normalization
        text_content = soup.get_text(separator='\n')
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        # Deduplication (very basic: keep unique lines, preserving order)
        seen = set()
        cleaned_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                cleaned_lines.append(line)
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Metadata Tagging
        metadata = {
            "source_url": url,
            "scheme_name": scheme_meta.get("name"),
            "category": scheme_meta.get("category"),
            "scrape_date": datetime.now().isoformat()
        }
        
        return {
            "metadata": metadata,
            "fund_details": fund_details,
            "sip_details": sip_details,
            "risk_info": risk_info,
            "tables": tables_data,
            "text": cleaned_text
        }

    def scrape_all_schemes(self):
        """Iterate over urls.json and scrape all 5 URLs"""
        with open(self.urls_file, 'r', encoding='utf-8') as f:
            urls_data = json.load(f)
            
        for scheme in urls_data.get('schemes', []):
            url = scheme['url']
            name = scheme['name']
            print(f"Processing: {name}")
            
            try:
                html = self.fetch(url)
                
                filename_base = name.lower().replace(" ", "_").replace("–", "").replace("-", "_")
                filename_base = re.sub(r'_+', '_', filename_base).strip('_')
                
                raw_path = os.path.join(self.raw_dir, f"{filename_base}.html")
                self.save_raw(html, raw_path)
                
                parsed_data = self.parse(html, url, scheme)
                
                processed_path = os.path.join(self.processed_dir, f"{filename_base}.json")
                self.save_processed(parsed_data, processed_path)
                
            except Exception as e:
                print(f"Failed to process {name}: {e}")
