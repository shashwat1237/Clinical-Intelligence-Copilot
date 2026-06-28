import os
import json
from groq import Groq
from app.core.config import settings

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile" 

    def generate_response(self, system_prompt: str, user_prompt: str, context: str) -> str:
        # Rebuilding the prompt block without string literals to bypass editor corruption
        NL = chr(10)
        messages = [
            {"role": "system", "content": f"{system_prompt}{NL}{NL}Context:{NL}{context}"},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {}