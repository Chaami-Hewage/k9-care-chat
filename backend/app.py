import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from pinecone_service import PineconeService
from gemini_service import GeminiService
from agent import VetAgent
from google_auth import GoogleAuthService
from calendar_service import CalendarService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Configure Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[Config.RATE_LIMIT_DEFAULT],
    storage_uri="memory://"
)

# Initialize Services & Agent
google_auth = GoogleAuthService()
calendar_service = CalendarService(auth_service=google_auth)
pinecone_service = PineconeService()
gemini_service = GeminiService()
agent = VetAgent(pinecone_service=pinecone_service, gemini_service=gemini_service, calendar_service=calendar_service)

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status."""
    return jsonify({
        "status": "healthy",
        "service": "Know Your Dog - Vet AI Agent",
        "gemini_connected": bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != "your_gemini_api_key_here"),
        "pinecone_connected": bool(pinecone_service.index is not None)
    }), 200

@app.route("/api/ask-vet", methods=["POST"])
@limiter.limit("20 per minute")
def ask_vet():
    """Main API endpoint for processing dog health queries."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. JSON body required."}), 400

        message = str(data.get("message", "")).strip()
        breed = str(data.get("breed", "Unknown Breed")).strip()
        age = str(data.get("age", "3")).strip()
        weight = str(data.get("weight", "20")).strip()
        email = str(data.get("email", "")).strip()

        # Input Validation & Sanitization
        if not message:
            return jsonify({"error": "Field 'message' cannot be empty."}), 400

        if len(message) > Config.MAX_INPUT_LENGTH:
            message = message[:Config.MAX_INPUT_LENGTH]

        logger.info(f"Processing ask-vet request for breed='{breed}', age='{age}', weight='{weight}'.")

        # Run AI Agent pipeline
        response_text = agent.analyze_and_respond(
            user_message=message,
            breed=breed,
            age=age,
            weight=weight,
            user_email=email
        )

        return jsonify({
            "answer": response_text,
            "breed": breed,
            "age": age,
            "weight": weight
        }), 200

    except Exception as e:
        logger.error(f"Unhandled error in ask_vet endpoint: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/api/auth/google/url", methods=["GET"])
def get_google_auth_url():
    url = google_auth.get_authorization_url()
    if url:
        return jsonify({"url": url}), 200
    return jsonify({"error": "Failed to generate auth url. Check config."}), 500

@app.route("/api/auth/google/callback", methods=["POST"])
def google_auth_callback():
    data = request.get_json()
    code = data.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    user_info = google_auth.handle_callback(code)
    if user_info:
        return jsonify({"user": user_info}), 200
    return jsonify({"error": "Failed to authenticate"}), 401

@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    email = request.args.get("email")
    if not email:
        return jsonify({"authenticated": False}), 400
    is_auth = google_auth.is_authenticated(email)
    return jsonify({"authenticated": is_auth}), 200

@app.route("/api/calendar/events", methods=["GET"])
def get_calendar_events():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    events = calendar_service.list_upcoming_reminders(email)
    return jsonify({"events": events}), 200

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Please wait a moment before sending another query."}), 429

if __name__ == "__main__":
    logger.info(f"Starting Flask Vet AI Agent server on port {Config.PORT}...")
    app.run(host="0.0.0.0", port=Config.PORT, debug=(Config.FLASK_ENV == "development"))
