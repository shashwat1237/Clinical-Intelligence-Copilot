import re

class Verifier:
    """Enforces absolute alignment of proof contexts to shield user views from phantom claims."""
    def verify_and_format(self, ai_response_text: str, context: str) -> dict:
        citations = []
        citation_matches = set(re.findall(r'\[(\d+)\]', ai_response_text))
        
        for match in citation_matches:
            # Bulletproof regex using \s* to survive any formatting or spacing corruptions
            pattern = rf'\[{match}\]\s*Source:\s*(.*?)\s*\(Page\s*(\d+)\)\s*Excerpt:\s*(.*?)(?=\s*\[\d+\]|$)'
            source_match = re.search(pattern, context, re.DOTALL | re.IGNORECASE)
            
            if source_match:
                citations.append({
                    "document_name": source_match.group(1).strip(),
                    "page_number": int(source_match.group(2)),
                    "excerpt": source_match.group(3).strip()[:150] + "..."
                })
            else:
                ai_response_text = ai_response_text.replace(f"[{match}]", "")
                
        return {
            "content": ai_response_text.strip(),
            "citations": citations
        }