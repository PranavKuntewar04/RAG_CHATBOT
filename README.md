# HDFC Mutual Fund FAQ Assistant (RAG Chatbot)

A Retrieval-Augmented Generation (RAG) chatbot designed to answer factual questions about HDFC Mutual Fund schemes using data scraped from Groww. It leverages ChromaDB for vector storage and Groq's LLM (`llama-3.3-70b-versatile`) for high-speed, accurate generation.

## Features

- **Facts-Only Responses**: Configured to provide short, factual answers (≤ 3 sentences).
- **Guardrails**: Built-in PII detection and refusal of investment advisory queries.
- **Source Citations**: Every generated answer includes the source URL and the date of the scraped data.
- **Modern UI**: Clean Streamlit interface matching HDFC AMC branding.

## Supported Schemes (HDFC Mutual Fund)

The chatbot is currently configured to provide information on the following 5 schemes from HDFC AMC:
1. HDFC Large Cap Fund – Direct Growth
2. HDFC Mid Cap Fund – Direct Growth
3. HDFC Small Cap Fund – Direct Growth
4. HDFC Gold ETF Fund of Fund – Direct Growth
5. HDFC Silver ETF FoF – Direct Growth

## Architecture Overview

The system follows a standard RAG (Retrieval-Augmented Generation) pipeline:
1. **Data Ingestion**: A web scraper extracts scheme details (NAV, AUM, expense ratio, SIP details, etc.) from Groww. The text is chunked using `RecursiveCharacterTextSplitter` and embedded using `BAAI/bge-small-en-v1.5`.
2. **Vector Store**: Embeddings and metadata are persisted in a local **ChromaDB** collection.
3. **Query Guardrails & Classifier**: User queries are intercepted to block PII and refuse advisory/opinion-based questions. Valid queries proceed to retrieval.
4. **Retriever**: The query is embedded and compared against the vector store using cosine similarity (top-k=3).
5. **Prompt Builder & LLM Generator**: Retrieved chunks are assembled into a strict system prompt and sent to the **Groq API** (`llama-3.3-70b-versatile`).
6. **Response Formatter**: The final response is validated (≤ 3 sentences) and returned to the Streamlit UI with proper source citations.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd RAG_CHATBOT
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

## How to Run

1. **Ingest Data (Phases 2 & 3)**:
   *Ensure you have scraped and chunked the data first.*
   ```bash
   # Run the scraper to fetch data from Groww
   python scraper/groww_scraper.py
   
   # Run the chunker and embedder to populate ChromaDB
   python embeddings/chunker.py
   python embeddings/vector_store.py
   ```

2. **Launch the Chatbot (Phase 7)**:
   Start the fully integrated pipeline and UI using the main entry point:
   ```bash
   python main.py
   ```
   *Alternatively, run Streamlit directly:*
   ```bash
   streamlit run ui/app.py
   ```

## Automated Daily Ingestion (Phase 8)

The project includes a GitHub Actions workflow (`.github/workflows/daily_ingestion.yml`) that runs daily at 10:30 AM IST (5:00 AM UTC). 
This workflow automatically:
1. Re-runs the web scraper to fetch the latest data from Groww.
2. Processes and chunks the data.
3. Updates the ChromaDB vector store.
4. Commits the updated ChromaDB files back to the repository.

You can also trigger this workflow manually from the "Actions" tab in GitHub.

## Known Limitations

- **DOM Dependency**: The bot relies heavily on the structure of Groww's HTML. If the DOM structure changes, the web scraper (`scraper/groww_scraper.py`) may need updates.
- **Limited Scope**: It only has context for the 5 selected HDFC Mutual Fund schemes. Questions outside these schemes will be flagged as out-of-scope.
- **Semantic Search Constraints**: Semantic search may occasionally miss highly specific numerical queries if the exact text wasn't embedded closely together during chunking.
