from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph.methods import Event

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

event_service = Event()

event_bp = Blueprint('events', __name__)

# Event routes.
# Create event route.
@event_bp.route('/events/create', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_name', 'description', 'date_time', 'max_players']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create event
        logger.info(f"<ml_service_run> Creating event: {data['event_name']}")
        event = event_service.create_event(
            event_name=data['event_name'],
            description=data['description'],
            date_time=data['date_time'],
            max_players=data['max_players'],
            current_players=data.get('current_players', 0)
        )
        
        if event:
            logger.info(f"<ml_service_run> Event created: {event}")
            return jsonify({
                "message": "Event created successfully",
                "event": event
            }), 201
        else:
            return jsonify({
                "error": "Failed to create event"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating event: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get event route.
@event_bp.route('/events/get', methods=['POST'])
def get_event():
    """Get an event by name"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'event_name' not in data:
            return jsonify({"error": "Missing required field: event_name"}), 400
        
        # Get event
        logger.info(f"<ml_service_run> Getting event: {data['event_name']}")
        event = event_service.get_event(event_name=data['event_name'])
        
        if event:
            logger.info(f"<ml_service_run> Event found: {event}")
            return jsonify({
                "message": "Event found successfully",
                "event": event
            }), 200
        else:
            return jsonify({
                "error": "Event not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting event: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get all events route.
@event_bp.route('/events/all', methods=['GET'])
def get_all_events():
    """Get all events"""
    try:
        logger.info("<ml_service_run> Getting all events")
        events = event_service.get_all_events()
        
        logger.info(f"<ml_service_run> Found {len(events)} events")
        return jsonify({
            "message": "Events retrieved successfully",
            "events": events,
            "count": len(events)
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting all events: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update event route.
@event_bp.route('/events/update', methods=['PUT'])
def update_event():
    """Update an event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'event_name' not in data:
            return jsonify({"error": "Missing required field: event_name"}), 400
        
        # Update event
        logger.info(f"<ml_service_run> Updating event: {data['event_name']}")
        event = event_service.update_event(
            event_name=data['event_name'],
            description=data.get('description'),
            date_time=data.get('date_time'),
            max_players=data.get('max_players'),
            current_players=data.get('current_players')
        )
        
        if event:
            logger.info(f"<ml_service_run> Event updated: {event}")
            return jsonify({
                "message": "Event updated successfully",
                "event": event
            }), 200
        else:
            return jsonify({
                "error": "Event not found or no updates provided"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error updating event: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Delete event route.
@event_bp.route('/events/delete', methods=['DELETE'])
def delete_event():
    """Delete an event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'event_name' not in data:
            return jsonify({"error": "Missing required field: event_name"}), 400
        
        # Delete event
        logger.info(f"<ml_service_run> Deleting event: {data['event_name']}")
        success = event_service.delete_event(event_name=data['event_name'])
        
        if success:
            logger.info(f"<ml_service_run> Event deleted: {data['event_name']}")
            return jsonify({
                "message": "Event deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "Event not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error deleting event: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Event hosted by field route.
@event_bp.route('/events/hosted-at-field', methods=['POST'])
def hosted_at_field():
    """Create a HOSTED_AT relationship between event and field"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_name', 'field_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create HOSTED_AT relationship
        logger.info(f"<ml_service_run> Creating HOSTED_AT relationship: {data['event_name']} -> {data['field_name']}")
        success = event_service.hosted_at_field(
            event_name=data['event_name'],
            field_name=data['field_name']
        )
        
        if success:
            logger.info(f"<ml_service_run> HOSTED_AT relationship created")
            return jsonify({
                "message": "Event hosted at field relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create hosted at field relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating hosted at field relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Event for sport route.
@event_bp.route('/events/for-sport', methods=['POST'])
def for_sport():
    """Create a FOR_SPORT relationship between event and sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_name', 'sport_name', 'min_skill_level']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate min_skill_level
        valid_skill_levels = ["Beginner", "Intermediate", "Advanced", "Competitive"]
        if data['min_skill_level'] not in valid_skill_levels:
            return jsonify({
                "error": f"Invalid min_skill_level. Must be one of: {', '.join(valid_skill_levels)}"
            }), 400
        
        # Create FOR_SPORT relationship
        logger.info(f"<ml_service_run> Creating FOR_SPORT relationship: {data['event_name']} -> {data['sport_name']}")
        success = event_service.for_sport(
            event_name=data['event_name'],
            sport_name=data['sport_name'],
            min_skill_level=data['min_skill_level']
        )
        
        if success:
            logger.info(f"<ml_service_run> FOR_SPORT relationship created")
            return jsonify({
                "message": "Event for sport relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create for sport relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating for sport relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500