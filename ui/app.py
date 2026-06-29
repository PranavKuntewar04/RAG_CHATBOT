import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://localhost:8000/api/chat"

# Set page configuration
st.set_page_config(
    page_title="HDFC Mutual Fund FAQ Assistant",
    page_icon="🏦",
    layout="centered",
)

# Custom CSS for styling
st.markdown("""
<style>
    .disclaimer-banner {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-weight: bold;
        border: 1px solid #ffeeba;
    }
    .citation {
        font-size: 0.8em;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Header
st.title("🏦 HDFC Mutual Fund FAQ Assistant")

# Disclaimer Banner
st.markdown('<div class="disclaimer-banner">⚠️ Facts-only. No investment advice.</div>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
Welcome! I can answer factual questions about HDFC Mutual Fund schemes.
""")

# Example questions
example_questions = [
    "What is the expense ratio of HDFC Mid Cap?",
    "What is the exit load of HDFC Equity Fund?",
    "What is the minimum SIP for HDFC Large Cap?"
]

st.markdown("**Try asking:**")
cols = st.columns(3)

# Handle example questions
prompt = None
for i, q in enumerate(example_questions):
    if cols[i].button(q, key=f"btn_{i}", use_container_width=True):
        prompt = q

# Chat input
user_input = st.chat_input("Type your question...")
if user_input:
    prompt = user_input

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("source_url"):
            st.markdown(f'<div class="citation">📎 Source: <a href="{message["source_url"]}" target="_blank">{message["source_url"]}</a><br>🕐 Last updated from sources: {message["last_updated"]}</div>', unsafe_allow_html=True)

# Handle new user input
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Call FastAPI backend
            response = requests.post(
                API_URL,
                json={"query": prompt, "session_id": st.session_state.session_id},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            answer = data["answer"]
            source_url = data.get("source_url", "")
            last_updated = data.get("last_updated", "")
            
            message_placeholder.markdown(answer)
            
            # Display citation
            if source_url and last_updated:
                st.markdown(f'<div class="citation">📎 Source: <a href="{source_url}" target="_blank">{source_url}</a><br>🕐 Last updated from sources: {last_updated}</div>', unsafe_allow_html=True)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "source_url": source_url,
                "last_updated": last_updated
            })
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Sorry, I couldn't reach the server. Please ensure the backend API is running. (Error: {str(e)})"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
