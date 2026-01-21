from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph import Sport

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

sport_service = Sport()

sport_bp = Blueprint('sports', __name__)

# Sport routes.
# Create sport route.
@sport_bp.route('/sports/create', methods=['POST'])
def create_sport():
    """Create a new sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sport_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create sport
        logger.info(f"<ml_service_run> Creating sport: {data['sport_name']}")
        sport = sport_service.create_sport(sport_name=data['sport_name'])
        
        if sport:
            logger.info(f"<ml_service_run> Sport created: {sport}")
            return jsonify({
                "message": "Sport created successfully",
                "sport": sport
            }), 201
        else:
            return jsonify({
                "error": "Failed to create sport"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating sport: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get sport route.
@sport_bp.route('/sports/get', methods=['POST'])
def get_sport():
    """Get a sport by name"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'sport_name' not in data:
            return jsonify({"error": "Missing required field: sport_name"}), 400
        
        # Get sport
        logger.info(f"<ml_service_run> Getting sport: {data['sport_name']}")
        sport = sport_service.get_sport(sport_name=data['sport_name'])
        
        if sport:
            logger.info(f"<ml_service_run> Sport found: {sport}")
            return jsonify({
                "message": "Sport found successfully",
                "sport": sport
            }), 200
        else:
            return jsonify({
                "error": "Sport not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting sport: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get all sports route.
@sport_bp.route('/sports/all', methods=['GET'])
def get_all_sports():
    """Get all sports"""
    try:
        logger.info("<ml_service_run> Getting all sports")
        sports = sport_service.get_all_sports()
        
        logger.info(f"<ml_service_run> Found {len(sports)} sports")
        return jsonify({
            "message": "Sports retrieved successfully",
            "sports": sports,
            "count": len(sports)
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting all sports: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update sport route.
@sport_bp.route('/sports/update', methods=['PUT'])
def update_sport():
    """Update a sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['old_sport_name', 'new_sport_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Update sport
        logger.info(f"<ml_service_run> Updating sport: {data['old_sport_name']} -> {data['new_sport_name']}")
        sport = sport_service.update_sport(
            old_sport_name=data['old_sport_name'],
            new_sport_name=data['new_sport_name']
        )
        
        if sport:
            logger.info(f"<ml_service_run> Sport updated: {sport}")
            return jsonify({
                "message": "Sport updated successfully",
                "sport": sport
            }), 200
        else:
            return jsonify({
                "error": "Sport not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error updating sport: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Delete sport route.
@sport_bp.route('/sports/delete', methods=['DELETE'])
def delete_sport():
    """Delete a sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'sport_name' not in data:
            return jsonify({"error": "Missing required field: sport_name"}), 400
        
        # Delete sport
        logger.info(f"<ml_service_run> Deleting sport: {data['sport_name']}")
        success = sport_service.delete_sport(sport_name=data['sport_name'])
        
        if success:
            logger.info(f"<ml_service_run> Sport deleted: {data['sport_name']}")
            return jsonify({
                "message": "Sport deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "Sport not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error deleting sport: {str(e)}")
        return jsonify({"error": str(e)}), 500

# For standalone running
if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(sport_bp)
    app.run(debug=True)
