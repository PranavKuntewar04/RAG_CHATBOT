import os
import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = os.path.join("data", "raw")
PARSED_DIR = os.path.join("data", "parsed")

def ensure_dirs():
    os.makedirs(PARSED_DIR, exist_ok=True)

def parse_html_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    
    if not script:
        logger.error(f"Could not find __NEXT_DATA__ in {file_path}")
        return None
        
    data = json.loads(script.string)
    mf = data.get("props", {}).get("pageProps", {}).get("mfServerSideData", {})
    
    if not mf:
        logger.error(f"Could not find mfServerSideData in {file_path}")
        return None
        
    scheme_name = mf.get("scheme_name", "")
    slug = file_path.split(os.sep)[-1].replace(".html", "")
    source_url = f"https://groww.in/mutual-funds/{slug}"
    
    risk_level = ""
    return_stats = mf.get("return_stats")
    if return_stats and isinstance(return_stats, list) and len(return_stats) > 0:
        risk_level = return_stats[0].get("risk", "")
    
    structured_data = {
        "nav": str(mf.get("nav", "")),
        "expense_ratio": str(mf.get("expense_ratio", "")) + "%" if mf.get("expense_ratio") else "",
        "exit_load": str(mf.get("exit_load", "")),
        "min_sip": str(mf.get("min_sip_investment", "")),
        "min_lumpsum": str(mf.get("min_investment_amount", "")),
        "benchmark": str(mf.get("benchmark_name", "")),
        "risk_level": str(risk_level),
        "fund_manager": str(mf.get("fund_manager", "")),
        "aum": str(mf.get("aum", "")),
        "category": str(mf.get("category", "")),
        "launch_date": str(mf.get("launch_date", ""))
    }
    
    # Generate sections based on structured data
    sections = [
        {
            "heading": "Fund Overview",
            "content": f"{scheme_name} has an NAV of ₹{structured_data['nav']} as of the latest data. It is a {structured_data['category']} fund managed by {structured_data['fund_manager']} with an AUM of ₹{structured_data['aum']} Cr. The fund was launched on {structured_data['launch_date']}. Its risk level is considered {structured_data['risk_level']}."
        },
        {
            "heading": "Fund Details",
            "content": f"Expense Ratio: {structured_data['expense_ratio']}. Exit Load: {structured_data['exit_load']} The minimum SIP amount is ₹{structured_data['min_sip']} and the minimum lumpsum amount is ₹{structured_data['min_lumpsum']}. Its benchmark is {structured_data['benchmark']}."
        }
    ]
    
    parsed_doc = {
        "scheme_name": scheme_name,
        "source_url": source_url,
        "category": str(mf.get("category", "")),
        "scrape_date": datetime.today().strftime("%Y-%m-%d"),
        "sections": sections,
        "structured_data": structured_data
    }
    
    return parsed_doc, slug

def parse_all():
    ensure_dirs()
    if not os.path.exists(RAW_DIR):
        logger.error(f"Raw directory {RAW_DIR} does not exist.")
        return
        
    for filename in os.listdir(RAW_DIR):
        if filename.endswith(".html"):
            file_path = os.path.join(RAW_DIR, filename)
            logger.info(f"Parsing {file_path}...")
            result = parse_html_file(file_path)
            if result:
                parsed_doc, slug = result
                out_path = os.path.join(PARSED_DIR, f"{slug}.json")
                with open(out_path, "w", encoding="utf-8") as out_f:
                    json.dump(parsed_doc, out_f, indent=2, ensure_ascii=False)
                logger.info(f"Saved parsed JSON to {out_path}")

if __name__ == "__main__":
    parse_all()
