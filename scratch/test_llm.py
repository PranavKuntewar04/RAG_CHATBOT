import os
import sys

# Add the project root to the path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generation.llm_client import generate
from src.generation.prompt_templates import SYSTEM_PROMPT

def run_test():
    print("--- Running LLM Integration Test ---\n")
    
    # 1. Simulate a user query
    user_query = "What is the expense ratio of the HDFC Mid Cap Fund?"
    print(f"User Query: {user_query}")
    
    # 2. Simulate the retrieved context from ChromaDB
    # In a real scenario, this comes from src/retrieval/vector_store.py
    mock_context = (
        "The expense ratio of HDFC Mid Cap Fund Direct Growth is 0.74%. "
        "The exit load is 1% for redemption within 1 year. "
        "Minimum SIP is Rs. 500."
    )
    print(f"Mock Retrieved Context:\n{mock_context}\n")
    
    # 3. Call the generation client
    print("Calling Groq LLM API (or mock if no key is set)...")
    try:
        response = generate(
            system_prompt=SYSTEM_PROMPT,
            user_query=user_query,
            context=mock_context
        )
        print(f"\n--- LLM Response ---\n{response}\n--------------------\n")
        
        print("Analysis:")
        if "Mock LLM Response" in response:
            print("Status: MOCK MODE (You haven't set GROQ_API_KEY in your .env file yet)")
        else:
            print("Status: SUCCESS (Received live response from Groq!)")
            if "0.74%" in response:
                print("Accuracy: Passed (The LLM correctly used the provided context)")
            else:
                print("Accuracy: Failed (The LLM hallucinated or missed the data)")
                
    except Exception as e:
        print(f"\nStatus: FAILED")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_test()
