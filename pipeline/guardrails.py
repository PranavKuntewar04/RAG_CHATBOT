import re
from typing import Optional

class Guardrails:
    PII_PATTERNS = {
        "PAN":     r"[A-Z]{5}[0-9]{4}[A-Z]",
        "Aadhaar": r"[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}",
        "Phone":   r"(?:\+91[\s-]?)?[6-9][0-9]{9}",
        "Email":   r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    }

    ADVISORY_KEYWORDS = [
        "should i", "recommend", "better", "best", "worth it",
        "good fund", "bad fund", "invest in", "buy", "sell",
        "compare returns", "which one", "suggest", "opinion",
        "prediction", "forecast", "will it grow"
    ]

    @classmethod
    def detect_pii(cls, query: str) -> Optional[str]:
        """
        Checks if the query contains PII. 
        Returns the type of PII detected, or None if safe.
        """
        for pii_type, pattern in cls.PII_PATTERNS.items():
            if re.search(pattern, query, re.IGNORECASE):
                return pii_type
        return None

    @classmethod
    def detect_advisory(cls, query: str) -> bool:
        """
        Checks if the query contains advisory keywords.
        Returns True if it's asking for advice, False otherwise.
        """
        query_lower = query.lower()
        for keyword in cls.ADVISORY_KEYWORDS:
            if keyword in query_lower:
                return True
        return False
