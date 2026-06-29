"""
Structured Attribute Chunking for mutual fund parsed data.

Why not RecursiveCharacterTextSplitter?
- Each parsed section is only ~200 chars — far below any reasonable chunk_size.
- The splitter would produce exactly 1 chunk per section with zero splitting.
- The structured_data fields (the most queryable data) would be completely ignored.

Instead, we create semantically focused chunks:
1. Attribute chunks  — one per structured_data field, as natural-language sentences
2. Section chunks    — one per section (already appropriately sized)
3. Full-doc chunk    — concatenation of all sections for broad queries

Expected output: ~14 chunks per scheme × 12 schemes = ~168 total chunks.
"""

import os
import json
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PARSED_DIR = os.path.join("data", "parsed")

# ---------------------------------------------------------------------------
# Human-readable templates for converting structured_data key-value pairs
# into natural-language sentences.
#
# This makes attribute chunks semantically similar to user queries like
# "What is the expense ratio of HDFC Mid Cap Fund?"
# ---------------------------------------------------------------------------
ATTRIBUTE_TEMPLATES = {
    "nav": "The NAV (Net Asset Value) of {scheme_name} is ₹{value}.",
    "expense_ratio": "The expense ratio of {scheme_name} is {value}.",
    "exit_load": "The exit load of {scheme_name}: {value}",
    "min_sip": "The minimum SIP amount for {scheme_name} is ₹{value}.",
    "min_lumpsum": "The minimum lumpsum investment for {scheme_name} is ₹{value}.",
    "benchmark": "The benchmark index for {scheme_name} is {value}.",
    "risk_level": "The risk level of {scheme_name} is {value}.",
    "fund_manager": "The fund manager(s) of {scheme_name}: {value}.",
    "aum": "The AUM (Assets Under Management) of {scheme_name} is ₹{value} Cr.",
    "category": "{scheme_name} belongs to the {value} category.",
    "launch_date": "{scheme_name} was launched on {value}.",
}


def chunk_document(parsed_doc: dict) -> list[dict]:
    """
    Convert a parsed JSON document into a list of chunks with metadata.

    Creates three types of chunks:
      1. Attribute chunks — one per structured_data field, phrased as a
         natural-language sentence so it aligns with user query embeddings.
      2. Section chunks   — one per section (Fund Overview, Fund Details).
         Each section is ~200 chars, already right-sized — no splitting needed.
      3. Full-document chunk — concatenation of all sections to catch broad
         or multi-attribute queries.

    Returns:
        list[dict]: Each dict has 'text' (str) and 'metadata' (dict) keys.
                    Metadata always includes: scheme_name, source_url,
                    category, scrape_date, chunk_type.
                    Attribute chunks also include 'attribute'.
                    Section chunks also include 'section'.
    """
    scheme_name = parsed_doc["scheme_name"]
    base_metadata = {
        "scheme_name": scheme_name,
        "source_url": parsed_doc["source_url"],
        "category": parsed_doc["category"],
        "scrape_date": parsed_doc["scrape_date"],
    }

    chunks = []

    # ── 1. Attribute chunks (from structured_data) ──────────────────────
    for field, value in parsed_doc.get("structured_data", {}).items():
        template = ATTRIBUTE_TEMPLATES.get(field)
        if template and value:
            text = template.format(scheme_name=scheme_name, value=value)
            chunks.append({
                "text": text,
                "metadata": {
                    **base_metadata,
                    "chunk_type": "attribute",
                    "attribute": field,
                },
            })

    # ── 2. Section chunks (whole sections, no splitting needed) ─────────
    for section in parsed_doc.get("sections", []):
        chunks.append({
            "text": section["content"],
            "metadata": {
                **base_metadata,
                "chunk_type": "section",
                "section": section["heading"],
            },
        })

    # ── 3. Full-document chunk (concatenated sections) ──────────────────
    full_text = " ".join(s["content"] for s in parsed_doc.get("sections", []))
    chunks.append({
        "text": full_text,
        "metadata": {
            **base_metadata,
            "chunk_type": "full_document",
        },
    })

    return chunks


def chunk_all(parsed_dir: str = PARSED_DIR) -> list[dict]:
    """
    Load all parsed JSON files from the given directory and chunk each one.

    Args:
        parsed_dir: Path to the directory containing parsed JSON files.

    Returns:
        list[dict]: Flat list of all chunks across all schemes.
    """
    if not os.path.exists(parsed_dir):
        logger.error(f"Parsed directory '{parsed_dir}' does not exist.")
        return []

    all_chunks = []
    schemes_processed = 0

    for filename in sorted(os.listdir(parsed_dir)):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(parsed_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                parsed_doc = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Skipping {filename}: {e}")
            continue

        chunks = chunk_document(parsed_doc)
        all_chunks.extend(chunks)
        schemes_processed += 1
        logger.info(
            f"Chunked {filename}: {len(chunks)} chunks "
            f"(scheme: {parsed_doc.get('scheme_name', 'unknown')})"
        )

    # ── Print summary ───────────────────────────────────────────────────
    type_counts = Counter(c["metadata"]["chunk_type"] for c in all_chunks)
    logger.info("-" * 50)
    logger.info("Chunking complete.")
    logger.info(f"  Schemes processed: {schemes_processed}")
    logger.info(f"  Attribute chunks:  {type_counts.get('attribute', 0)}")
    logger.info(f"  Section chunks:    {type_counts.get('section', 0)}")
    logger.info(f"  Full-doc chunks:   {type_counts.get('full_document', 0)}")
    logger.info(f"  Total chunks:      {len(all_chunks)}")

    return all_chunks


if __name__ == "__main__":
    import sys
    # Windows console defaults to cp1252 which can't print ₹ — force UTF-8
    sys.stdout.reconfigure(encoding="utf-8")

    chunks = chunk_all()
    if chunks:
        # Print a few sample chunks for visual inspection
        print("\n== Sample chunks (first 3) ==========================")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n[{i}] type={chunk['metadata']['chunk_type']}")
            print(f"    text: {chunk['text'][:120]}...")
            meta_preview = {k: v for k, v in chunk['metadata'].items() if k != 'source_url'}
            print(f"    metadata: {meta_preview}")

