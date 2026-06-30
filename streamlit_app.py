import os
import streamlit as st
import uuid
from src.guardrails.input_guard import classify_query
from src.guardrails.output_guard import validate_output
from src.retrieval.vector_store import query as vector_query, collection
from src.generation.llm_client import generate
from src.generation.prompt_templates import (
    SYSTEM_PROMPT, REFUSAL_PII, REFUSAL_ADVISORY,
    REFUSAL_PROMPT_INJECTION, REFUSAL_TOO_LONG
)
from src.ingestion.embedder import embed_query

# Load Streamlit secrets into environment variables
if hasattr(st, "secrets"):
    for key, value in st.secrets.items():
        os.environ[key] = str(value)

@st.cache_resource(show_spinner="Loading data & embedding model (first time only)...")
def initialize_pipeline():
    """Run ingestion once per app session. Cached so it survives reruns."""
    from scripts.run_ingestion import main as run_ingestion
    run_ingestion()
    return True

# This runs once when the app starts, then is cached
initialize_pipeline()

# Page config
st.set_page_config(
    page_title="HDFC Mutual Fund FAQ Assistant",
    page_icon="🏦",
    layout="centered",
)

# Custom CSS
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

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Header
st.title("🏦 HDFC Mutual Fund FAQ Assistant")
st.markdown(
    '<div class="disclaimer-banner">⚠️ Facts-only. No investment advice.</div>',
    unsafe_allow_html=True,
)

# Example questions
example_questions = [
    "What is the expense ratio of HDFC Mid Cap?",
    "What is the exit load of HDFC Equity Fund?",
    "What is the minimum SIP for HDFC Large Cap?",
]
st.markdown("**Try asking:**")
cols = st.columns(3)
prompt = None
for i, q in enumerate(example_questions):
    if cols[i].button(q, key=f"btn_{i}", use_container_width=True):
        prompt = q

user_input = st.chat_input("Type your question...")
if user_input:
    prompt = user_input

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("source_url"):
            st.markdown(
                f'<div class="citation">📎 Source: <a href="{message["source_url"]}" target="_blank">{message["source_url"]}</a>'
                f'<br>🕐 Last updated from sources: {message["last_updated"]}</div>',
                unsafe_allow_html=True,
            )

# Handle new input — all logic runs in-process
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # 1. Classify
            intent = classify_query(prompt)
            refusals = {
                "PII_DETECTED": REFUSAL_PII,
                "ADVISORY": REFUSAL_ADVISORY,
                "PROMPT_INJECTION": REFUSAL_PROMPT_INJECTION,
                "TOO_LONG": REFUSAL_TOO_LONG,
            }
            if intent in refusals:
                answer = refusals[intent]
                message_placeholder.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                # 2. Embed + Retrieve
                query_embedding = embed_query(prompt)
                results = vector_query(query_embedding=query_embedding, top_k=5)

                if not results or not results.get("documents") or not results["documents"][0]:
                    answer = "I don't have enough information to answer that."
                    message_placeholder.markdown(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                else:
                    chunks = results["documents"][0]
                    metadatas = results["metadatas"][0]
                    context = "\\n\\n".join(f"Document: {doc}" for doc in chunks)
                    top_meta = metadatas[0] if metadatas else {}
                    source_url = top_meta.get("source_url", "")
                    scrape_date = top_meta.get("scrape_date", "Unknown")

                    # 3. Generate
                    raw_answer = generate(
                        system_prompt=SYSTEM_PROMPT,
                        user_query=prompt,
                        context=context,
                    )

                    # 4. Validate
                    validated = validate_output(
                        answer=raw_answer,
                        source_url=source_url,
                        scrape_date=scrape_date,
                    )
                    answer = validated["answer"]
                    message_placeholder.markdown(answer)

                    if validated["source_url"] and validated["last_updated"]:
                        st.markdown(
                            f'<div class="citation">📎 Source: <a href="{validated["source_url"]}" target="_blank">{validated["source_url"]}</a>'
                            f'<br>🕐 Last updated from sources: {validated["last_updated"]}</div>',
                            unsafe_allow_html=True,
                        )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "source_url": validated["source_url"],
                        "last_updated": validated["last_updated"],
                    })
        except Exception as e:
            error_msg = f"Sorry, something went wrong: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
