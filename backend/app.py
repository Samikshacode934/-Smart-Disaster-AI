from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import services.gee_data_fetcher as gee_data_fetcher
from transformers import pipeline
import tensorflow_hub as hub
import tensorflow as tf

tf.config.set_visible_devices([], 'GPU')  # Hide GPU
physical_devices = tf.config.list_physical_devices('CPU')  # Use CPU only

# Load environment variables
load_dotenv()

# Initialize Flask with custom template and static folders
app = Flask(
    __name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static'
            )


# --- AI Models Initialization ---
# Free disaster classifier (small CPU-friendly model)
disaster_clf = pipeline("image-classification", 
                       model="microsoft/resnet-50")

# Free text embedding model
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4" )

# --- MongoDB Connection with Error Handling ---
try:
    client = MongoClient(os.getenv("ATLAS_URI"))
    db = client["disaster_db"]
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    # Exit if DB connection fails
    exit(1)

# Mock ML function
def predict_disaster(image_url):
    return {"type": "flood", "confidence": 0.95}

# Embedding generator function
def generate_embedding(text):
    # Returns a list, convert to python list for MongoDB compatibility
    return embed([text])[0].numpy().tolist()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/detect", methods=["POST"])
def detect_disaster():
    try:
        data = request.json
        if not data or "image_url" not in data:
            return jsonify({"error": "Missing image_url"}), 400
            
            # Get AI prediction
        prediction = predict_disaster(data["image_url"])
        
        # Generate description embedding
        description = f"{prediction['type']} disaster at location"
        embedding = generate_embedding(description)

        # Insert into MongoDB
        db.disasters.insert_one({
            "type": prediction["type"],
            "location": {"type": "Point", "coordinates": [77.2, 28.6]},
            "timestamp": datetime.now(),
            "confidence": prediction["confidence"]
        })
        
        return jsonify({
    "status": "success",
    "inserted_id": str(result.inserted_id),  
    "prediction": prediction
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_similar_disasters", methods=["POST"])
def get_similar():
    """Vector search endpoint"""
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
        disasters = list(results)
        return jsonify(disasters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/disasters")
def get_disasters():
    try:
        disasters = list(db.disasters.find({}, {"_id": 0}))  # Exclude _id for cleaner JSON
        return jsonify(disasters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)