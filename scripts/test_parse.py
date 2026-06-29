import sys
from bs4 import BeautifulSoup
import re

def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    data = {}
    data['scheme_name'] = soup.find('h1').text.strip() if soup.find('h1') else None
    
    text = soup.get_text(separator='|', strip=True)
    parts = [p.strip() for p in text.split('|') if p.strip()]
    
    for i, part in enumerate(parts):
        lower_part = part.lower()
        if 'nav' in lower_part and lower_part == 'nav':
            # next few parts might contain the value
            print("NAV near:", parts[i:i+5])
        elif 'expense ratio' in lower_part:
            print("Expense ratio near:", parts[i:i+5])
        elif 'exit load' in lower_part:
            print("Exit load near:", parts[i:i+5])
        elif 'fund size' in lower_part or 'aum' in lower_part:
            print("AUM near:", parts[i:i+5])

if __name__ == "__main__":
    parse_html(sys.argv[1])
