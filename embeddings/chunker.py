import json
import os
import sys
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add parent directory to path so config can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentChunker:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " "]
        )

    def chunk_document(self, processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunks the preprocessed document into smaller text segments with metadata.
        """
        metadata = processed_data.get("metadata", {})
        text = processed_data.get("text", "")
        
        # Include tables/details in chunking if they are present
        extra_content = []
        for key in ["fund_details", "sip_details", "risk_info"]:
            info = processed_data.get(key, {})
            if info:
                extra_content.append(f"{key.replace('_', ' ').title()}:")
                for k, v in info.items():
                    extra_content.append(f"{k}: {v}")
                    
        # Append extra content to text if any
        if extra_content:
            text = "\n".join(extra_content) + "\n\n" + text

        chunks = self.splitter.split_text(text)
        
        result_chunks = []
        for i, chunk in enumerate(chunks):
            scheme_name = metadata.get("scheme_name", "unknown")
            base_id = scheme_name.lower().replace(" ", "-").replace("–", "").replace("--", "-").strip("-")
            chunk_id = f"{base_id}-{i:03d}"
            
            chunk_metadata = {
                "chunk_id": chunk_id,
                "source_url": metadata.get("source_url", ""),
                "scheme_name": scheme_name,
                "scrape_date": metadata.get("scrape_date", ""),
            }
            
            result_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk,
                "metadata": chunk_metadata
            })
            
        return result_chunks
        
    def chunk_all_documents(self, data_dir: str) -> List[Dict[str, Any]]:
        """
        Process all JSON files in the given directory.
        """
        all_chunks = []
        if not os.path.exists(data_dir):
            return all_chunks
            
        for filename in sorted(os.listdir(data_dir)):
            if filename.endswith(".json"):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        chunks = self.chunk_document(data)
                        all_chunks.extend(chunks)
                    except json.JSONDecodeError as e:
                        print(f"Error reading {filename}: {e}")
        return all_chunks

if __name__ == "__main__":
    chunker = DocumentChunker()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, "data", "processed")
    chunks = chunker.chunk_all_documents(processed_dir)
    print(f"Total chunks created: {len(chunks)}")
    if chunks:
        print("Sample chunk metadata:", chunks[0]["metadata"])
        print("Sample chunk text:", repr(chunks[0]["text"][:100] + "..."))
        
        # Save chunks to a file for manual review
        chunks_dir = os.path.join(base_dir, "data", "chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        out_path = os.path.join(chunks_dir, "all_chunks.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"Saved all chunks to {out_path} for review.")
