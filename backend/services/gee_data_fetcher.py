import ee
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import tensorflow as tf

# 1. Configure environment to suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TensorFlow messages
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU usage completely

# 2. Earth Engine Initialization (Simplified)
def initialize_earth_engine():
    """Initialize Earth Engine with fallback to browser auth"""
    try:
        ee.Initialize()
        print("✅ Earth Engine initialized successfully")
        return True
    except ee.EEException:
        print("⚠️ Earth Engine not authenticated - running one-time setup...")
        try:
            # This will open browser for authentication
            ee.Authenticate(auth_mode="notebook")
            ee.Initialize()
            print("✅ Earth Engine authenticated and initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Earth Engine: {str(e)}")
            print("Please run this command manually in your terminal:")
            print("  earthengine authenticate")
            return False

# 3. Initialize services
if not initialize_earth_engine():
    exit(1)

# MongoDB Connection
load_dotenv()
try:
    client = MongoClient(os.getenv("ATLAS_URI"))
    db = client["disaster_db"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit(1)

# 4. Simplified AI Model Loading
def load_landcover_model():
    """Load model with better error handling"""
    try:
        # Using lightweight MobileNetV2 instead of heavy ResNet for hackathon
        model = tf.keras.applications.MobileNetV2(weights='imagenet')
        print("✅ AI Model loaded successfully")
        return model
    except Exception as e:
        print(f"❌ Failed to load AI model: {e}")
        return None

# 5. Optimized Data Processing
def process_disaster_data():
    """Main processing function with better error handling"""
    try:
        india_bbox = ee.Geometry.BBox(68.0, 8.0, 97.0, 37.0)
        
        # Get recent Sentinel-2 data (last 30 days)
        sentinel = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
            .filterBounds(india_bbox) \
            .filterDate(ee.Date(datetime.now().strftime('%Y-%m-%d')).advance(-30, 'day'), 
                        ee.Date(datetime.now())) \
            .first()
        
        # Flood detection
        ndwi = sentinel.normalizedDifference(['B3', 'B8'])
        flood_areas = ndwi.gt(0.2).selfMask()
        
        # Get simplified flood vectors
        floods = flood_areas.reduceToVectors(
            geometry=india_bbox,
            scale=500,  # Lower resolution for faster processing
            maxPixels=1e8
        )
        
        # Process and store data
        features = floods.getInfo().get('features', [])
        store_disasters(features, 'flood')
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")

def store_disasters(features, disaster_type):
    """Store disaster data with batch processing"""
    docs = []
    for feature in features:
        try:
            coords = feature['geometry']['coordinates'][0][0]  # First point
            docs.append({
                "type": disaster_type,
                "location": {
                    "type": "Point",
                    "coordinates": [coords[0], coords[1]]
                },
                "timestamp": datetime.utcnow(),
                "confidence": 0.85,  # Default confidence
                "source": "satellite"
            })
        except Exception as e:
            print(f"Skipping invalid feature: {e}")

    if docs:
        try:
            db.disasters.insert_many(docs)
            print(f"✅ Inserted {len(docs)} {disaster_type} events")
        except Exception as e:
            print(f"❌ Failed to insert documents: {e}")

if __name__ == "__main__":
    process_disaster_data()