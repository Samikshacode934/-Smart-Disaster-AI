from flask import Blueprint, jsonify, request
from backend.services.gee_data_fetcher import EarthEngineService
from backend.services.gee_data_fetcher import process_disaster_data
from backend.utils.logger import logger

disaster_bp = Blueprint('disaster', __name__, url_prefix='/api/v1')

@disaster_bp.route('/disasters', methods=['GET'])
def get_disasters():
    try:
        bbox = request.args.get('bbox', '68.0,8.0,97.0,37.0')  # Default India bbox
        days = int(request.args.get('days', 1))
        
        ee_service = EarthEngineService()
        data = ee_service.get_combined_data(bbox, days)
        
        processed = process_disaster_data(data)
        return jsonify({
            "status": "success",
            "data": processed
        })
    except Exception as e:
        logger.error(f"Error in get_disasters: {str(e)}")
        raise

@disaster_bp.route('/detect', methods=['POST'])
def detect_disaster():
    try:
        # Implementation for image detection
        pass
    except Exception as e:
        logger.error(f"Error in detect_disaster: {str(e)}")
        raise