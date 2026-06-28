from app.agents.verifier import Verifier

def test_hallucinated_citation_removal():
    verifier = Verifier()
    context = "[1] Source: Doc A (Page 1)nExcerpt: Heart rate normal."
    # Model hallucinated [2]
    ai_text = "Heart is fine [1], but liver is failing [2]."
    
    res = verifier.verify_and_format(ai_text, context)
    assert len(res["citations"]) == 1
    # Ensure hallucinated marker [2] is stripped from content
    assert "[2]" not in res["content"]

