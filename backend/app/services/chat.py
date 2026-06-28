from sqlalchemy.orm import Session
from app.agents.planner import Planner
from app.agents.router import Router
from app.agents.verifier import Verifier
from app.db import models_and_crud
from app.ai.groq_client import GroqClient

class ChatService:
    def __init__(self, db: Session, user_id: str, patient_id: str):
        self.db = db
        self.user_id = user_id
        self.patient_id = patient_id
        self.groq = GroqClient()
        self.planner = Planner()
        self.router = Router(db, patient_id)
        self.verifier = Verifier()

    def process_user_query(self, message: str) -> dict:
        """Agent Orchestration Layer: Planner -> Router -> LLM -> Verifier"""
        # Save user message
        models_and_crud.save_chat_message(self.db, self.patient_id, "user", message)
        
        # 1. Planner: Determine intent and required data
        plan = self.planner.analyze_intent(message)
        
        # 2. Router: Fetch minimal required context
        context = self.router.assemble_context(message, plan)
        
        # 3. AI Reasoning
        system_prompt = (
            "You are a strict clinical data assistant. Use ONLY the provided context to answer. "
            "Do not diagnose. YOU MUST append citations to your claims using the exact format [1], [2], etc., "
            "corresponding to the source index numbers provided in the context."
        )
        ai_response_text = self.groq.generate_response(system_prompt, message, context)
        
        # 4. Verifier: Ensure grounding and format citations
        verified_response = self.verifier.verify_and_format(ai_response_text, context)
        
        # Save and return AI message
        saved_msg = models_and_crud.save_chat_message(
            self.db, 
            self.patient_id, 
            "ai", 
            verified_response["content"], 
            verified_response["citations"]
        )
        
        return {
            "role": saved_msg.role, 
            "content": saved_msg.content, 
            "citations": saved_msg.citations_json
        }

