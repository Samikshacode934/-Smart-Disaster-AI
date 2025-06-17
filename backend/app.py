from flask import Flask, render_template, request, jsonify
from huggingface_hub import Collection
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import services.gee_data_fetcher as gee_data_fetcher
from transformers import MODEL_FOR_NEXT_SENTENCE_PREDICTION_MAPPING, pipeline
import tensorflow_hub as hub
import tensorflow as tf
from bson import json_util

# TensorFlow configuration
tf.config.set_visible_devices([], 'GPU')
physical_devices = tf.config.list_physical_devices('CPU')

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

# --- AI Models ---
disaster_clf = pipeline("image-classification", model="microsoft/resnet-50")
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# --- MongoDB Setup ---
try:
    client = MongoClient(os.getenv("ATLAS_URI"))
    db = client["disaster_db"]
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    exit(1)

# --- Helper Functions ---
def predict_disaster(image_url):
    # You could replace this with `disaster_clf(image_url)` in a real app
    return {"type": "flood", "confidence": 0.95}

def generate_embedding(text):
    return embed([text])[0].numpy().tolist()

# --- Routes ---
@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        image_url = data.get('image_url')

        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400

        # Your existing detection logic here...
        prediction = MODEL_FOR_NEXT_SENTENCE_PREDICTION_MAPPING(image_url)  # hypothetical function

        # Save to MongoDB
        result = Collection.insert_one({
            'type': prediction['type'],
            'confidence': prediction['confidence'],
            'image_url': image_url,
            'timestamp': datetime.utcnow(),
            'location': {
                'type': 'Point',
                'coordinates': [78.6569, 22.9734]  # Default/mock coords
            }
        })

        return jsonify({
            'prediction': prediction,
            'inserted_id': str(result.inserted_id)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route("/api/disasters")
def get_disasters():
    try:
        disasters = list(db.disasters.find({}, {"_id": 0}))
        return app.response_class(
            response=json_util.dumps(disasters),
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error fetching disasters: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/ping")
def ping():
    return "pong"

@app.route("/get_similar_disasters", methods=["POST"])
def get_similar():
    try:
        data = request.json
        query_embed = generate_embedding(data["description"])
        results = db.disasters.aggregate([{
            "$vectorSearch": {
                "index": "disaster_vec_index",
                "path": "embedding",
                "queryVector": query_embed,
                "numCandidates": 100,
                "limit": 3
            }
        }])
        return jsonify(list(results))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
