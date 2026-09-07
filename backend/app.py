import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from pinecone_service import PineconeService
from gemini_service import GeminiService
from agent import VetAgent

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
pinecone_service = PineconeService()
gemini_service = GeminiService()
agent = VetAgent(pinecone_service=pinecone_service, gemini_service=gemini_service)

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
            weight=weight
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

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Please wait a moment before sending another query."}), 429

if __name__ == "__main__":
    logger.info(f"Starting Flask Vet AI Agent server on port {Config.PORT}...")
    app.run(host="0.0.0.0", port=Config.PORT, debug=(Config.FLASK_ENV == "development"))
