from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging

# Import blueprints from route modules
from knowledge_graph.routes.user_route import user_bp
from knowledge_graph.routes.sport_route import sport_bp
from knowledge_graph.routes.event_route import event_bp
from knowledge_graph.routes.field_route import field_bp
from knowledge_graph.routes.post_route import post_bp
from knowledge_graph.routes.rag_route import rag_bp
from knowledge_graph.methods import User

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Create main Flask app
app = Flask(__name__)
CORS(app)

# Create user service instance for routes defined in this file
user_service = User()

# Register all blueprints
app.register_blueprint(user_bp)
app.register_blueprint(sport_bp)
app.register_blueprint(event_bp)
app.register_blueprint(field_bp)
app.register_blueprint(post_bp)
app.register_blueprint(rag_bp)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "ml_service"}), 200

@app.route('/', methods=['GET'])
def index():
    """API root endpoint"""
    return jsonify({
        "message": "JuegaLink ML Service API",
        "endpoints": {
            "users": "/users/*",
            "sports": "/sports/*",
            "events": "/events/*",
            "fields": "/fields/*",
            "health": "/health"
        }
    }), 200

@app.route('/users/update', methods=['PUT', 'PATCH'])
def update_user():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data:
            return jsonify({"error": "Missing required field: username"}), 400
        
        # Update user
        logger.info(f"<ml_service_run> Updating user: {data['username']}")
        user = user_service.update_user(
            username=data['username'],
            age=data.get('age'),
            city=data.get('city'),
            state=data.get('state'),
            bio=data.get('bio'),
            email=data.get('email'),
            phone_no=data.get('phone_no')
        )
        
        if user:
            logger.info(f"<ml_service_run> User updated: {user}")
            return jsonify({
                "message": "User updated successfully",
                "user": user
            }), 200
        else:
            return jsonify({
                "error": "No fields to update or user not found"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error updating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/users/<username>/friends', methods=['GET'])
def get_user_friends(username):
    """Get friends count for a user"""
    try:
        friends = user_service.get_friends(username)
        return jsonify({
            "friends": friends,
            "count": len(friends)
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting friends: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    """Get a user by username"""
    try:
        user = user_service.get_user(username)
        if user:
            return jsonify({
                "user": user
            }), 200
        else:
            return jsonify({
                "error": "User not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting user: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    logger.info(f"Starting ML Service on port {port}")
    app.run(debug=True, port=port, host='0.0.0.0')