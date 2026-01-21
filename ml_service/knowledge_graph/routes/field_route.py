from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph import Field

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

field_service = Field()

field_bp = Blueprint('fields', __name__)

# Field routes.
# Create field route.
@field_bp.route('/fields/create', methods=['POST'])
def create_field():
    """Create a new field"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['field_name', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create field
        logger.info(f"<ml_service_run> Creating field: {data['field_name']}")
        field = field_service.create_field(
            field_name=data['field_name'],
            address=data['address']
        )
        
        if field:
            logger.info(f"<ml_service_run> Field created: {field}")
            return jsonify({
                "message": "Field created successfully",
                "field": field
            }), 201
        else:
            return jsonify({
                "error": "Failed to create field"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating field: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get field route.
@app.route('/fields/get', methods=['POST'])
def get_field():
    """Get a field by name"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'field_name' not in data:
            return jsonify({"error": "Missing required field: field_name"}), 400
        
        # Get field
        logger.info(f"<ml_service_run> Getting field: {data['field_name']}")
        field = field_service.get_field(field_name=data['field_name'])
        
        if field:
            logger.info(f"<ml_service_run> Field found: {field}")
            return jsonify({
                "message": "Field found successfully",
                "field": field
            }), 200
        else:
            return jsonify({
                "error": "Field not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting field: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get field by address route.
@app.route('/fields/get-by-address', methods=['POST'])
def get_field_by_address():
    """Get a field by address"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'address' not in data:
            return jsonify({"error": "Missing required field: address"}), 400
        
        # Get field
        logger.info(f"<ml_service_run> Getting field by address: {data['address']}")
        field = field_service.get_field_by_address(address=data['address'])
        
        if field:
            logger.info(f"<ml_service_run> Field found: {field}")
            return jsonify({
                "message": "Field found successfully",
                "field": field
            }), 200
        else:
            return jsonify({
                "error": "Field not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting field by address: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get all fields route.
@app.route('/fields/all', methods=['GET'])
def get_all_fields():
    """Get all fields"""
    try:
        logger.info("<ml_service_run> Getting all fields")
        fields = field_service.get_all_fields()
        
        logger.info(f"<ml_service_run> Found {len(fields)} fields")
        return jsonify({
            "message": "Fields retrieved successfully",
            "fields": fields,
            "count": len(fields)
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting all fields: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update field route.
@app.route('/fields/update', methods=['PUT'])
def update_field():
    """Update a field"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'field_name' not in data:
            return jsonify({"error": "Missing required field: field_name"}), 400
        
        # Update field
        logger.info(f"<ml_service_run> Updating field: {data['field_name']}")
        field = field_service.update_field(
            field_name=data['field_name'],
            address=data.get('address'),
            new_field_name=data.get('new_field_name')
        )
        
        if field:
            logger.info(f"<ml_service_run> Field updated: {field}")
            return jsonify({
                "message": "Field updated successfully",
                "field": field
            }), 200
        else:
            return jsonify({
                "error": "Field not found or no updates provided"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error updating field: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Delete field route.
@app.route('/fields/delete', methods=['DELETE'])
def delete_field():
    """Delete a field"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['field_name', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Delete field
        logger.info(f"<ml_service_run> Deleting field: {data['field_name']} at {data['address']}")
        success = field_service.delete_field(
            field_name=data['field_name'],
            address=data['address']
        )
        
        if success:
            logger.info(f"<ml_service_run> Field deleted: {data['field_name']}")
            return jsonify({
                "message": "Field deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "Field not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error deleting field: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Field supports sport route.
@app.route('/fields/supports-sport', methods=['POST'])
def supports_sport():
    """Create a SUPPORTS relationship between field and sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['field_name', 'sport_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create SUPPORTS relationship
        logger.info(f"<ml_service_run> Creating SUPPORTS relationship: {data['field_name']} -> {data['sport_name']}")
        success = field_service.supports_sport(
            field_name=data['field_name'],
            sport_name=data['sport_name']
        )
        
        if success:
            logger.info(f"<ml_service_run> SUPPORTS relationship created")
            return jsonify({
                "message": "Field supports sport relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create supports sport relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating supports sport relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# For standalone running
if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(field_bp)
    app.run(debug=True)
