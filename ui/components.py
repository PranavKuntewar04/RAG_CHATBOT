import streamlit as st
import os

def load_css():
    """Load the custom CSS styling."""
    css_file = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_header():
    """Render the application header."""
    st.title("🏦 HDFC Mutual Fund FAQ Assistant")

def render_disclaimer():
    """Render the persistent disclaimer banner."""
    st.markdown(
        """
        <div class="disclaimer-banner">
            ⚠️ <b>Disclaimer:</b> This assistant provides facts based on official documentation only. It does NOT provide investment advice, recommendations, or opinions.
        </div>
        """,
        unsafe_allow_html=True
    )

def render_example_questions():
    """Render the 3 clickable example questions and return the selected query if any."""
    st.write("📋 **Example Questions:**")
    
    col1, col2, col3 = st.columns(3)
    
    selected_query = None
    with col1:
        if st.button("What is the expense ratio of HDFC Large Cap Fund?"):
            selected_query = "What is the expense ratio of HDFC Large Cap Fund?"
            
    with col2:
        if st.button("What is the exit load for HDFC Small Cap Fund?"):
            selected_query = "What is the exit load for HDFC Small Cap Fund?"
            
    with col3:
        if st.button("What is the min SIP for HDFC Mid Cap Fund?"):
            selected_query = "What is the minimum SIP amount for HDFC Mid Cap Fund?"
            
    return selected_query

def render_chat_message(role, content, citation=None, footer=None):
    """Render a single chat message, optionally with citation and footer."""
    with st.chat_message(role):
        st.markdown(content)
        
        if citation:
            st.markdown(f'<a href="{citation}" target="_blank" class="citation-link">View Source Document</a>', unsafe_allow_html=True)
            
        if footer:
            st.markdown(f'<div class="response-footer">{footer}</div>', unsafe_allow_html=True)
