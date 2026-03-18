from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from flasgger import Swagger
import json
import os
import numpy as np
from endee_client import EndeeClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Swagger setup for API documentation
swagger_config = {
    "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}
swagger = Swagger(app, config=swagger_config, template={"info": {"title": "Smart Food App API", "version": "1.0"}})

# Endee DB setup
ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080")
ENDEE_TOKEN = os.getenv("ENDEE_TOKEN", "endee_token")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "food_items")

client = EndeeClient(base_url=ENDEE_URL, auth_token=ENDEE_TOKEN)

# Load the AI model for vector embeddings
print("Starting up AI model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Simple list to keep track of what the user searched for this session
search_history = []

def detect_diet_type(query, explicit_type=None):
    # Check if user specifically asked for veg or non-veg
    if explicit_type in ["veg", "non-veg"]:
        return explicit_type
    
    q = query.lower()
    # Looking for non-veg keywords first
    non_veg_words = ["non veg", "chicken", "mutton", "fish", "meat", "egg"]
    if any(word in q for word in non_veg_words):
        return "non-veg"
    
    # Then veg keywords
    veg_words = ["veg", "vegetarian", "paneer", "dal", "aloo"]
    if any(word in q for word in veg_words):
        return "veg"
    
    return None

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "Food App API is online"})

@app.route('/search', methods=['GET'])
def search():
    """
    Semantic search for dishes.
    """
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    food_type = request.args.get('type')
    
    if not query:
        return jsonify({"results": []})
    
    search_history.append(query)
    if len(search_history) > 5: search_history.pop(0)
    
    # Determine if we should filter by diet
    diet = detect_diet_type(query, food_type)
    
    # Convert query to vector
    vector = model.encode([query])[0]
    
    # Get matches from Endee
    res = client.search(COLLECTION_NAME, vector.tolist(), limit=20)
    results = res.get('results', [])
    
    # Post-search filtering to be 100% sure about veg/non-veg
    final_list = []
    for item in results:
        meta = json.loads(item.get('meta', '{}'))
        if diet and meta.get('type') != diet:
            continue
            
        # Add basic scoring and reasons
        score = item.get('score', 0)
        reason = f"Matches your interest in '{query}'"
        if meta.get('rating') > 4.5:
            reason += " and it's highly rated!"
            
        final_list.append({
            **meta,
            "match_score": score,
            "explanation": reason
        })
        
    return jsonify({"results": final_list[:limit], "detected_type": diet})

@app.route('/recommend', methods=['GET'])
def recommend():
    """
    Personalized suggestions based on what you searched for.
    """
    diet = request.args.get('type')
    
    # Create a context vector from recent searches
    context = " ".join(search_history) if search_history else "popular tasty dishes"
    vector = model.encode([context])[0]
    
    res = client.search(COLLECTION_NAME, vector.tolist(), limit=15)
    items = []
    for r in res.get('results', []):
        meta = json.loads(r.get('meta', '{}'))
        if diet and meta.get('type') != diet:
            continue
        items.append({**meta, "match_score": r.get('score', 0)})
        
    return jsonify({
        "items": items[:6],
        "message": "Suggestions based on your history" if search_history else "Trending now"
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(port=port, debug=True)
