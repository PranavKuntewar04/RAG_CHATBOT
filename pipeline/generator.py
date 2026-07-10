import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMGenerator:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.1, max_tokens: int = 200):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """
        Send assembled prompt to LLM.
        Return raw text response.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return "I apologize, but I am currently unable to process your request due to a technical error."
