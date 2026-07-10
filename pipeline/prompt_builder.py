import os
import sys
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.prompts import SYSTEM_PROMPT

class PromptBuilder:
    def build_prompt(self, user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Assemble the three-part prompt:
        1. SYSTEM PROMPT
        2. CONTEXT (top retrieved chunks)
        3. USER QUERY
        """
        
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            # Extract metadata and text
            meta = chunk.get("metadata", {})
            text = chunk.get("text", "")
            scheme = meta.get("scheme_name", "Unknown Scheme")
            
            context_parts.append(f"--- Context {i+1} ({scheme}) ---\n{text}")
            
        context_str = "\n\n".join(context_parts)
        if not context_str:
            context_str = "No relevant context found."
            
        prompt = f"""{SYSTEM_PROMPT}

Context:
{context_str}

User Query: {user_query}"""

        return prompt
