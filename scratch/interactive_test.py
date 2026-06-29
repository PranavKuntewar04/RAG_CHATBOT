import os
import sys

# Add the project root to the path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generation.llm_client import generate
from src.generation.prompt_templates import SYSTEM_PROMPT

def run_interactive():
    print("=========================================")
    print("       Interactive LLM Testing           ")
    print("=========================================")
    print("Type 'exit' or 'quit' to stop.")
    print("Press Ctrl+C to force exit.\n")
    
    # We provide a slightly expanded mock context so you have a few things to ask about
    mock_context = (
        "The expense ratio of HDFC Mid Cap Fund Direct Growth is 0.74%. "
        "The exit load is 1% for redemption within 1 year. "
        "Minimum SIP is Rs. 500. "
        "The fund manager is Chirag Setalvad. "
        "It belongs to the Mid Cap category."
    )
    print(f"Loaded Mock Context:\n{mock_context}\n")
    print("-" * 40)

    while True:
        try:
            user_query = input("\nYour question: ").strip()
            if user_query.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            
            if not user_query:
                continue
                
            response = generate(
                system_prompt=SYSTEM_PROMPT,
                user_query=user_query,
                context=mock_context
            )
            print(f"\nResponse:\n{response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    run_interactive()
