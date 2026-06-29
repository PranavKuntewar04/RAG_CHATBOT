def validate_output(answer: str, source_url: str, scrape_date: str) -> dict:
    """
    Post-processes the LLM output to ensure guardrail compliance.
    Caps sentences at 3, checks for advisory language, and appends citations.
    """
    # 1. Cap sentences at 3
    # A simple split by '. ' to approximate sentences.
    sentences = answer.split('. ')
    if len(sentences) > 3:
        answer = '. '.join(sentences[:3])
        if not answer.endswith('.'):
            answer += '.'
            
    # 2. Scan for advisory language
    advisory_words = ["recommend", "should", "best", "i suggest", "better"]
    answer_lower = answer.lower()
    for word in advisory_words:
        if word in answer_lower:
            answer = "I can only share verified facts. For investment guidance, please consult a SEBI-registered advisor."
            break
            
    # 3. Ensure citation link exists (if not replaced by advisory fallback)
    if "I can only share verified facts." not in answer:
        if source_url and source_url not in answer:
            answer += f"\n\nSource: {source_url}"
        
        # 4. Ensure footer exists
        footer = f"Last updated from sources: {scrape_date}"
        if footer not in answer:
            answer += f"\n\n{footer}"
        
    return {
        "answer": answer,
        "source_url": source_url,
        "last_updated": scrape_date
    }
