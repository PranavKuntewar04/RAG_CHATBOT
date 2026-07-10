import os
import sys
from typing import Dict, Any

# Add parent directory to path so guardrails can be imported if needed directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.guardrails import Guardrails

class QueryClassifier:
    
    OOS_KEYWORDS = ["weather", "cricket", "movie", "politics", "recipe", "sports"]
    COMPARISON_KEYWORDS = ["compare", "vs", "versus", "better than"]

    @classmethod
    def classify(cls, query: str) -> Dict[str, Any]:
        """
        Classifies the user query into intent categories and provides
        a corresponding action or refusal message if necessary.
        """
        # 1. Check for PII
        pii_type = Guardrails.detect_pii(query)
        if pii_type:
            return {
                "classification": "PII_DETECTED",
                "message": f"🚫 I detected sensitive information ({pii_type}) in your query. For your privacy, please remove it and try again."
            }

        # 2. Check for Advisory intent
        if Guardrails.detect_advisory(query):
            return {
                "classification": "ADVISORY",
                "message": "🚫 I am a facts-only FAQ assistant and cannot provide investment advice, recommendations, or opinions. Please consult a SEBI-registered financial advisor or visit the [AMFI Investor Education Portal](https://www.amfiindia.com/investor-corner) for general guidance."
            }
            
        # 3. Check for Comparison intent
        query_lower = query.lower()
        if any(kw in query_lower for kw in cls.COMPARISON_KEYWORDS):
            return {
                "classification": "COMPARISON",
                "message": "🚫 I cannot provide direct comparisons between funds. Please refer to the official [HDFC Mutual Fund Factsheets](https://www.hdfcfund.com/information/fact-sheet) for detailed performance metrics."
            }

        # 4. Check for Out-of-scope intent (very basic rule-based check)
        if any(kw in query_lower for kw in cls.OOS_KEYWORDS):
            return {
                "classification": "OUT_OF_SCOPE",
                "message": "🔄 I specialize in answering factual questions about HDFC Mutual Fund schemes. I cannot help with topics outside of mutual funds and investments."
            }

        # 5. Default to FACTUAL (safe to proceed to retrieval pipeline)
        return {
            "classification": "FACTUAL",
            "message": None
        }

if __name__ == "__main__":
    queries = [
        "What is the expense ratio of HDFC Large Cap?",
        "Should I invest in HDFC small cap or mid cap?",
        "My PAN is ABCDE1234F, what should I do?",
        "How is the weather today?",
        "Compare HDFC Mid cap vs Small cap"
    ]
    
    classifier = QueryClassifier()
    for q in queries:
        res = classifier.classify(q)
        print(f"Q: '{q}'")
        print(f"  Classification: {res['classification']}")
        if res['message']:
            print(f"  Response: {res['message']}")
        print("-" * 50)
