from openai import OpenAI
from src.config import settings

# Groq uses an OpenAI-compatible API
client = OpenAI(
    api_key=settings.GROQ_API_KEY or "dummy_key_for_testing",
    base_url="https://api.groq.com/openai/v1",
)

def generate(system_prompt: str, user_query: str, context: str) -> str:
    formatted_prompt = system_prompt.format(
        retrieved_chunks=context,
        user_query=user_query,
    )
    
    # Check if API key is missing (for local testing without a real key)
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        return f"[Mock LLM Response for: {user_query}]\nBased on the context, this is a simulated response because GROQ_API_KEY is not configured."
        
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": user_query},
        ],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )
    return response.choices[0].message.content
