import logging
from typing import Dict, Any
from pinecone_service import PineconeService
from gemini_service import GeminiService
from calendar_service import CalendarService
from vaccine_engine import VaccineEngine

logger = logging.getLogger(__name__)

RED_FLAG_KEYWORDS = [
    "chocolate", "grapes", "raisins", "xylitol", "rat poison", "antifreeze",
    "bloat", "unconscious", "seizure", "collapsed", "cannot breathe", "choking",
    "bleeding heavily", "hit by car"
]

class VetAgent:
    def __init__(self, pinecone_service: PineconeService, gemini_service: GeminiService, calendar_service: CalendarService):
        self.pinecone = pinecone_service
        self.gemini = gemini_service
        self.calendar = calendar_service

    def analyze_and_respond(self, user_message: str, breed: str, age: str, weight: str, user_email: str = "") -> str:
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
            
        email_instruction = ""
        if user_email:
            email_instruction = f"The user is authenticated with Google Calendar. Their email is '{user_email}'. DO NOT ask for their email, just use this one when calling tools."
        else:
            email_instruction = "The user is NOT authenticated. If they ask to book an appointment or schedule vaccines, YOU MUST ask for their email address first."

        # Step 3: Build System Prompt tailored to Dog Profile & Breed
        system_prompt = (
            f"You are 'Dr. Paws', an expert, warm, and highly knowledgeable veterinary assistant copilot.\n"
            f"Dog Profile Details:\n"
            f"- Breed: {breed}\n"
            f"- Age: {age} years old\n"
            f"- Weight: {weight} kg\n"
            f"{knowledge_context}\n\n"
            f"Instructions:\n"
            f"1. Maintain a very warm, friendly, and conversational human tone throughout. Talk like a real, caring vet talking to a pet parent. Avoid sounding robotic, dry, or overly clinical.\n"
            f"2. Provide empathetic, accurate, clear, and actionable advice tailored specifically to a {age}-year-old, {weight}kg {breed}.\n"
            f"3. Note breed-specific vulnerabilities or diet/exercise nuances if relevant.\n"
            f"4. Use structured formatting with markdown (bullet points, bold key steps) so it's easy to read.\n"
            f"5. Always include practical home-care steps, warning signs to watch out for, and when to visit an emergency vet.\n"
            f"6. Include a brief friendly disclaimer that this is AI guidance and not a substitute for an in-person physical vet examination.\n"
            f"7. CRITICAL: DO NOT introduce yourself or say 'Hello there! Dr. Paws here'. The user already knows you. Jump directly into your advice.\n"
            f"8. If the illness seems serious, or if the user requests it, book a vet appointment.\n"
            f"9. If the user asks about vaccines, schedule them on their calendar.\n\n"
            f"Auth Status: {email_instruction}"
        )

        def book_vet_appointment(email: str, reason: str, date: str, time: str = "10:00") -> str:
            """
            Book a vet appointment for the dog on Google Calendar.
            Use this ONLY when the illness seems serious or when the user explicitly requests an appointment.
            
            Args:
                email: The user's Google email address for the calendar invite. YOU MUST ASK THE USER FOR THIS if you don't know it.
                reason: Short description of why they are visiting the vet.
                date: The date in YYYY-MM-DD format. Assume the current year is 2026.
                time: The time in HH:MM format (24-hour).
            """
            result = self.calendar.create_vet_appointment(
                email=email,
                dog_name=f"{breed}",
                reason=reason,
                date=date,
                time=time
            )
            if result:
                return f"Successfully booked appointment on {date} at {time}. Event link: {result.get('link')}"
            return "Failed to book the appointment. The user's email might not be authorized or there was a calendar error."

        def schedule_vaccines(email: str) -> str:
            """
            Schedule upcoming and future vaccines for the dog on Google Calendar based on their breed and age.
            Use this when the user asks about vaccines or asks to schedule them.
            
            Args:
                email: The user's Google email address. YOU MUST ASK THE USER FOR THIS if you don't know it.
            """
            try:
                age_float = float(age)
            except ValueError:
                age_float = 3.0
            
            schedule = VaccineEngine.get_vaccine_schedule(breed=breed, age_years=age_float)
            created_events = []
            
            for v in schedule.get('upcoming', []) + schedule.get('future', []):
                res = self.calendar.create_vaccine_reminder(
                    email=email,
                    dog_name=f"{breed}",
                    vaccine_name=v['vaccine'],
                    due_date=v['due_date'],
                    notes=v['description']
                )
                if res:
                    created_events.append(f"{v['vaccine']} on {v['due_date']}")
                    
            if created_events:
                summary = "Scheduled the following vaccines on Calendar:\n" + "\n".join([f"- {c}" for c in created_events])
                return summary
            return "No vaccines needed scheduling, or failed to access calendar. They might be fully up to date."

        tools = [book_vet_appointment, schedule_vaccines]

        # Step 4: Generate LLM Response
        llm_response = self.gemini.generate_response(
            system_instruction=system_prompt,
            prompt=user_message,
            tools=tools
        )

        return f"{emergency_warning}{llm_response}"
