from app.agents.verifier import Verifier

def test_verifier_citation_logic():
    verifier = Verifier()
    context = "[1] Source: BloodReport.pdf (Page 2)nExcerpt: Glucose is 110."
    ai_text = "Your glucose is slightly elevated [1]."
    
    res = verifier.verify_and_format(ai_text, context)
    assert len(res["citations"]) == 1
    assert res["citations"][0]["page_number"] == 2
    assert res["citations"][0]["document_name"] == "BloodReport.pdf"

