import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("ATLAS_URI", "mongodb://localhost:27017/disaster_db")
    GEE_PROJECT = os.getenv("GEE_PROJECT", "smart-disaster-ai")
    MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 3600))  # 1 hour