"""Save all chunked data to data/chunked/ as JSON files."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import json
from src.ingestion.chunker import chunk_all

CHUNKED_DIR = os.path.join("data", "chunked")
os.makedirs(CHUNKED_DIR, exist_ok=True)

# Generate all chunks
chunks = chunk_all()

# Group chunks by scheme_name
grouped = {}
for chunk in chunks:
    scheme = chunk["metadata"]["scheme_name"]
    grouped.setdefault(scheme, []).append(chunk)

# Save per-scheme files
for scheme_name, scheme_chunks in grouped.items():
    slug = scheme_name.replace(" ", "-").lower()
    path = os.path.join(CHUNKED_DIR, f"{slug}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scheme_chunks, f, indent=2, ensure_ascii=False)

# Save combined file with all chunks
all_path = os.path.join(CHUNKED_DIR, "all_chunks.json")
with open(all_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(chunks)} chunks to {CHUNKED_DIR}/")
print(f"  Per-scheme files: {len(grouped)}")
print(f"  Combined file:    {all_path}")
