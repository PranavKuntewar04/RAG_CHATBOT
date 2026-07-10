import streamlit as st
import sys
import os

# Streamlit Cloud uses an older sqlite3 version which breaks ChromaDB. 
# This workaround overrides it with pysqlite3.
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# Add parent directory to path so pipeline can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components import load_css, render_header, render_disclaimer, render_example_questions, render_chat_message

# We will initialize the actual pipeline components in Phase 7 (main.py) or here.
# For now, we will set up the UI skeleton and state management.

def initialize_session_state():
    """Initialize Streamlit session state for chat history."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I am the HDFC Mutual Fund FAQ Assistant. How can I help you today?",
            "citation": None,
            "footer": None
        })

@st.cache_resource
def get_pipeline():
    """Initialize and cache the pipeline components."""
    from pipeline.retriever import Retriever
    from pipeline.prompt_builder import PromptBuilder
    from pipeline.generator import LLMGenerator
    from pipeline.response_formatter import ResponseFormatter
    
    return {
        "retriever": Retriever(),
        "prompt_builder": PromptBuilder(),
        "generator": LLMGenerator(),
        "formatter": ResponseFormatter()
    }

def handle_user_input(prompt: str):
    """Process user input, update chat history, and generate a response."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    render_chat_message("user", prompt)

    from pipeline.query_classifier import QueryClassifier

    with st.spinner("Searching for answers..."):
        # 1. Classify the query
        classification_result = QueryClassifier.classify(prompt)
        
        if classification_result["classification"] != "FACTUAL":
            # If not factual (e.g. advisory, PII), return the guardrail message
            msg = classification_result["message"]
            st.session_state.messages.append({
                "role": "assistant",
                "content": msg,
                "citation": None,
                "footer": None
            })
            render_chat_message("assistant", msg)
            return

        try:
            # Get cached pipeline
            pipeline = get_pipeline()
            
            # 2. Retrieve context chunks
            chunks = pipeline["retriever"].retrieve(prompt)
            
            # 3. Build the prompt
            llm_prompt = pipeline["prompt_builder"].build_prompt(prompt, chunks)
            
            # 4. Generate the response
            raw_response = pipeline["generator"].generate(llm_prompt)
            
            # 5. Format the response (extract citation and date from top chunk)
            top_chunk = chunks[0] if chunks else {}
            metadata = top_chunk.get("metadata", {})
            source_url = metadata.get("source_url", "No Source URL")
            scrape_date = metadata.get("scrape_date", "Unknown Date")
            
            formatted = pipeline["formatter"].format_response(raw_response, source_url, scrape_date)
            
            answer = formatted["answer"]
            citation = formatted["citation"]
            footer = formatted["footer"]
            
        except Exception as e:
            answer = f"An error occurred while processing your request: {e}"
            citation = None
            footer = None

        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citation": citation,
            "footer": footer
        })
        
        render_chat_message("assistant", answer, citation, footer)


def main():
    # Setup page configuration
    st.set_page_config(
        page_title="HDFC MF FAQ Assistant",
        page_icon="🏦",
        layout="centered"
    )

    # Load UI styling and components
    load_css()
    render_header()
    render_disclaimer()

    # Initialize chat history
    initialize_session_state()

    # Display example questions and capture click
    selected_example = render_example_questions()
    
    st.markdown("---")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        render_chat_message(
            message["role"], 
            message["content"], 
            message.get("citation"), 
            message.get("footer")
        )

    # Accept user input
    user_input = st.chat_input("Ask a question about HDFC Mutual Funds...")
    
    # Process example question click or manual input
    if selected_example:
        handle_user_input(selected_example)
    elif user_input:
        handle_user_input(user_input)

if __name__ == "__main__":
    main()
