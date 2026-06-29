# src/generation/response_builder.py

def build_response(raw_answer: str, source_url: str, scrape_date: str) -> dict:
    return {
        "answer": raw_answer.strip(),
        "source_url": source_url,
        "last_updated": scrape_date,
    }
