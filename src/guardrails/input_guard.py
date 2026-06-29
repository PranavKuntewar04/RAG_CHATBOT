import re

# PII patterns
PAN_REGEX = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]')
AADHAAR_REGEX = re.compile(r'\d{4}\s?\d{4}\s?\d{4}')
PHONE_REGEX = re.compile(r'(\+91[\-\s]?)?[6-9]\d{9}')
EMAIL_REGEX = re.compile(r'[\w.-]+@[\w.-]+\.\w+')

# Advisory keywords
ADVISORY_KEYWORDS = [
    "should i", "recommend", "is better", "best fund",
    "suggest", "good investment", "worth investing", "buy or sell",
    "better option", "compare performance"
]

# Prompt injection keywords
PROMPT_INJECTION_KEYWORDS = [
    "ignore previous", "system prompt", "pretend you are"
]

def classify_query(query: str) -> str:
    """
    Classifies the user query intent to determine if it should be blocked by guardrails.
    Returns one of: PII_DETECTED, PROMPT_INJECTION, ADVISORY, TOO_LONG, or FACTUAL.
    """
    if len(query) > 500:
        return "TOO_LONG"
        
    query_lower = query.lower()
    
    # 1. PII check (highest priority)
    if (PAN_REGEX.search(query) or AADHAAR_REGEX.search(query) or 
        PHONE_REGEX.search(query) or EMAIL_REGEX.search(query)):
        return "PII_DETECTED"
        
    # 2. Prompt injection check
    if any(kw in query_lower for kw in PROMPT_INJECTION_KEYWORDS):
        return "PROMPT_INJECTION"
    
    # 3. Advisory check
    if any(kw in query_lower for kw in ADVISORY_KEYWORDS):
        return "ADVISORY"
    
    # 4. Scope check could go here, but for now we default to FACTUAL
    
    return "FACTUAL"
