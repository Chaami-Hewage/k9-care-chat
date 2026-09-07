import logging
from config import Config

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.client = None
        self.legacy_model = None
        self._init_gemini()

    def _init_gemini(self):
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_gemini_api_key_here":
            logger.warning("GEMINI_API_KEY is not set. Gemini API calls will require valid key.")
            return

        try:
            # First try official google-genai package
            from google import genai
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            logger.info("Initialized Google GenAI client.")
        except Exception as e:
            logger.info(f"Trying google-generativeai fallback: {e}")
            try:
                import google.generativeai as genai
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.legacy_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Initialized google.generativeai legacy model.")
            except Exception as legacy_err:
                logger.error(f"Failed to initialize Gemini SDK: {legacy_err}")

    def generate_response(self, system_instruction: str, prompt: str) -> str:
        """
        Generate response from Gemini given system instruction and user prompt.
        """
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_gemini_api_key_here":
            return (
                "⚠️ **Backend Key Missing**: Please set your `GEMINI_API_KEY` in `backend/.env` "
                "to enable live AI vet responses. (Get a free key at [Google AI Studio](https://aistudio.google.com/))."
            )

        try:
            if self.client:
                # Using google.genai
                response = self.client.models.generate_content(
                    model=Config.GEMINI_MODEL,
                    contents=f"{system_instruction}\n\nUser Query: {prompt}",
                )
                return response.text
            elif self.legacy_model:
                # Using google.generativeai
                full_prompt = f"{system_instruction}\n\nUser Query: {prompt}"
                response = self.legacy_model.generate_content(full_prompt)
                return response.text
            else:
                # Dynamic re-attempt initialization if key was updated dynamically
                self._init_gemini()
                if self.client or self.legacy_model:
                    return self.generate_response(system_instruction, prompt)
                return "Gemini service is currently unavailable. Please check your API key configuration."
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"I encountered an error communicating with Gemini AI: {str(e)}"
