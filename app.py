import os
import json
import time
from functools import wraps

# 1. LOAD DOTENV BEFORE ANY CLIENT INITIALIZATION
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from config import Config
from models import db, bcrypt, ReadingBook
from routes.auth import auth_bp
from routes.books import books_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)

# 2. SAFELY INITIALIZE GEMINI AI WITH EXPLICIT API KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
ai_client = None

if GEMINI_API_KEY:
    try:
        from google import genai
        from google.genai import types
        # Passing api_key explicitly prevents falling back to GCP/ADC OAuth tokens (401 error)
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Gemini AI initialized successfully!")
    except Exception as e:
        print(f"❌ Gemini Init Error: {e}")
else:
    print("⚠️ GEMINI_API_KEY not found in environment.")

# Rate Limiter
def rate_limit(max_calls=5, period=60):
    def decorator(f):
        calls = []
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            if len(calls) >= max_calls:
                return jsonify({"error": "Rate limit exceeded. Try again in a minute."}), 429
            calls.append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/api/reading-dna', methods=['GET'])
@jwt_required()
def get_reading_dna():
    if not ai_client:
        return jsonify({"traits": [], "message": "AI disabled"}), 200

    try:
        user_id = int(get_jwt_identity())
        user_books = ReadingBook.query.filter_by(user_id=user_id).all()

        if not user_books:
            return jsonify({"traits": [], "message": "Add rated books to unlock DNA!"}), 200

        library_summary = ", ".join([
            f"{b.title} ({b.rating} stars)" for b in user_books if getattr(b, 'rating', None)
        ])

        prompt = f"""
        Analyze book ratings: {library_summary}.
        Generate a 'Reading DNA' profile with 5 traits/genres and percentage match (0-100%).
        Return strictly valid JSON:
        {{ "traits": [{{"name": "Thriller", "percentage": 90}}] }}
        """

        try:
            response = ai_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return jsonify(data), 200
        except Exception as e:
            print(f"AI/JSON Error: {e}")
            return jsonify({"traits": [{"name": "Avid Reader", "percentage": 80}]}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/recommendations', methods=['POST'])
@jwt_required()
@rate_limit(max_calls=5, period=60)
def get_recommendations():
    if not ai_client:
        return jsonify({"recommendations": [], "message": "AI disabled"}), 200

    try:
        user_id = int(get_jwt_identity())
        user_query = (request.get_json() or {}).get('prompt', '')

        if not user_query:
            return jsonify({"error": "Prompt required"}), 400

        user_books = ReadingBook.query.filter_by(user_id=user_id).all()
        library_summary = ", ".join([b.title for b in user_books])

        prompt = f"""
        User Library: {library_summary}
        User Request: "{user_query}"
        Recommend 3 books matching request. Return strictly valid JSON:
        {{ "recommendations": [{{"title": "Book", "author": "Author", "match_percentage": 90, "reason": "Why"}}] }}
        """

        try:
            response = ai_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return jsonify(data), 200
        except Exception as e:
            print(f"AI/JSON Error: {e}")
            return jsonify({"recommendations": []}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "ai_enabled": ai_client is not None}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)