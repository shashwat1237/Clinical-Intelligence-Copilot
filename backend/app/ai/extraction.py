from app.ai.groq_client import GroqClient
from app.ai.prompts import EXTRACTION_SYSTEM_PROMPT
from app.core.config import logger

def extract_clinical_entities_from_text(text: str) -> dict:
    """
    Transforms raw medical text into structured JSON clinical entities and timeline events.
    """
    client = GroqClient()
    
    # FIX: Replaced corrupted 'nn' with explicit structural newline characters 
    NL = chr(10)
    user_prompt = f"Extract clinical entities and timeline events from the following medical report:{NL}{NL}{text}"
    
    try:
        extracted_json = client.generate_json(EXTRACTION_SYSTEM_PROMPT, user_prompt)
        # Ensure fallback structure if model hallucinated keys
        return {
            "entities": extracted_json.get("entities", []),
            "timeline": extracted_json.get("timeline", [])
        }
    except Exception as e:
        logger.error(f"Failed to extract entities: {e}")
        return {"entities": [], "timeline": []}