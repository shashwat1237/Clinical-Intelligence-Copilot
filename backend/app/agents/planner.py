from app.ai.groq_client import GroqClient
from app.ai.prompts import ROUTER_DECISION_PROMPT
from app.core.config import logger

class Planner:
    """
    Agent Layer: Determines HOW a question should be answered.
    """
    def __init__(self):
        self.groq = GroqClient()

    def analyze_intent(self, user_question: str) -> dict:
        logger.info(f"Planner analyzing intent for: {user_question}")
        try:
            plan = self.groq.generate_json(ROUTER_DECISION_PROMPT, user_question)
            return {
                "strategy": plan.get("strategy", "HYBRID"),
                "entities_to_search": plan.get("entities_to_search", [])
            }
        except Exception as e:
            logger.error(f"Planner failed, defaulting to HYBRID: {e}")
            return {"strategy": "HYBRID", "entities_to_search": []}

