import re
from typing import Dict, Any

class ResponseFormatter:
    def format_response(self, raw_response: str, source_url: str, scrape_date: str) -> Dict[str, str]:
        """
        Post-process every LLM response to ensure compliance.
        """
        
        # 1. Truncate to <= 3 sentences
        sentences = re.split(r'(?<=[.!?]) +', raw_response.strip())
        truncated_sentences = sentences[:3]
        truncated_response = ' '.join(truncated_sentences)
        
        # 2. Check for advisory language (basic safety net, even though prompt says facts-only)
        advisory_keywords = [
            "recommend", "advise", "suggest", "better", "best", "should invest", "good choice", "bad choice"
        ]
        
        has_advice = any(word in truncated_response.lower() for word in advisory_keywords)
        if has_advice:
            truncated_response = "I cannot provide investment advice or recommendations. " + truncated_response
            
        return {
            "answer": truncated_response,
            "citation": source_url,
            "footer": f"Last updated from sources: {scrape_date}"
        }
