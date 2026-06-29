"""Analyze chunk statistics to inform embedding model selection."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json

chunks = json.load(open("data/chunked/all_chunks.json", "r", encoding="utf-8"))
lengths = [len(c["text"]) for c in chunks]

print(f"Total chunks: {len(chunks)}")
print(f"Char lengths - min: {min(lengths)}, max: {max(lengths)}, avg: {sum(lengths)/len(lengths):.0f}, median: {sorted(lengths)[len(lengths)//2]}")

for ctype in ["attribute", "section", "full_document"]:
    subset = [c for c in chunks if c["metadata"]["chunk_type"] == ctype]
    if subset:
        lens = [len(c["text"]) for c in subset]
        print(f"\n{ctype} chunks ({len(subset)}):")
        print(f"  avg: {sum(lens)/len(lens):.0f} chars (~{sum(lens)/len(lens)/4:.0f} tokens)")
        print(f"  min: {min(lens)} chars, max: {max(lens)} chars")
        print(f"  sample: {subset[0]['text'][:80]}...")

print(f"\nOverall estimated tokens (chars/4): avg ~{sum(lengths)/len(lengths)/4:.0f}, max ~{max(lengths)/4:.0f}")
print(f"\nUnique scheme names: {len(set(c['metadata']['scheme_name'] for c in chunks))}")
print(f"Unique attributes: {sorted(set(c['metadata'].get('attribute','') for c in chunks if c['metadata']['chunk_type']=='attribute'))}")
