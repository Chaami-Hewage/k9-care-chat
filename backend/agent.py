import logging
from typing import Dict, Any
from pinecone_service import PineconeService
from gemini_service import GeminiService

logger = logging.getLogger(__name__)

RED_FLAG_KEYWORDS = [
    "chocolate", "grapes", "raisins", "xylitol", "rat poison", "antifreeze",
    "bloat", "unconscious", "seizure", "collapsed", "cannot breathe", "choking",
    "bleeding heavily", "hit by car"
]

class VetAgent:
    def __init__(self, pinecone_service: PineconeService, gemini_service: GeminiService):
        self.pinecone = pinecone_service
        self.gemini = gemini_service

    def analyze_and_respond(self, user_message: str, breed: str, age: str, weight: str) -> str:
        """
        Agentic pipeline:
        1. Emergency Red-Flag detection
        2. Knowledge Retrieval (Pinecone Vector DB RAG)
        3. Tailored Contextual System Prompting
        4. LLM Generation (Gemini)
        """
        # Step 1: Emergency red-flag check
        lowered_message = user_message.lower()
        emergency_warning = ""
        for keyword in RED_FLAG_KEYWORDS:
            if keyword in lowered_message:
                emergency_warning = (
                    "🚨 **EMERGENCY WARNING**: Your message mentions symptoms or toxic substances that may require immediate emergency veterinary attention! "
                    "Please contact your local emergency vet clinic or emergency pet helpline immediately.\n\n"
                )
                break

        # Step 2: RAG Vector Knowledge Search
        knowledge_snippets = self.pinecone.search_knowledge(query=user_message, breed=breed)
        knowledge_context = ""
        if knowledge_snippets:
            knowledge_context = "\n\nRetrieved Knowledge Base Context:\n" + "\n".join(
                [f"- {k.get('text', '')}" for k in knowledge_snippets]
            )

        # Step 3: Build System Prompt tailored to Dog Profile & Breed
        system_prompt = (
            f"You are 'Dr. Paws', an expert, warm, and highly knowledgeable veterinary assistant copilot.\n"
            f"Dog Profile Details:\n"
            f"- Breed: {breed}\n"
            f"- Age: {age} years old\n"
            f"- Weight: {weight} kg\n"
            f"{knowledge_context}\n\n"
            f"Instructions:\n"
            f"1. Provide empathetic, accurate, clear, and actionable advice tailored specifically to a {age}-year-old, {weight}kg {breed}.\n"
            f"2. Note breed-specific vulnerabilities or diet/exercise nuances if relevant.\n"
            f"3. Use structured formatting with markdown (bullet points, bold key steps).\n"
            f"4. Always include practical home-care steps, warning signs to watch out for, and when to visit an emergency vet.\n"
            f"5. Maintain a friendly, supportive, reassuring tone for the dog owner.\n"
            f"6. Include a brief friendly disclaimer that this is AI guidance and not a substitute for in-person physical vet examination."
        )

        # Step 4: Generate LLM Response
        llm_response = self.gemini.generate_response(
            system_instruction=system_prompt,
            prompt=user_message
        )

        return f"{emergency_warning}{llm_response}"
