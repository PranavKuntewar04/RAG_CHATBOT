import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    print("Loading configuration...")
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("GROQ_API_KEY"):
        print("WARNING: GROQ_API_KEY is not set in the environment.")
        print("Please add it to your .env file before proceeding.")
        return

    # Determine paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "ui", "app.py")
    
    if not os.path.exists(app_path):
        print(f"Error: Streamlit app not found at {app_path}")
        return

    print("Launching Streamlit UI...")
    # Note: Streamlit will handle initializing the Vector Store, Embedder, and LLM 
    # internally using @st.cache_resource in app.py to avoid re-initialization on every rerun.
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except subprocess.CalledProcessError as e:
        print(f"Streamlit process failed: {e}")

if __name__ == "__main__":
    main()
