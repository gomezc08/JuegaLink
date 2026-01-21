from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging

# Import blueprints from route modules
from knowledge_graph.routes.user_route import user_bp
from knowledge_graph.routes.sport_route import sport_bp
from knowledge_graph.routes.event_route import event_bp
from knowledge_graph.routes.field_route import field_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Create main Flask app
app = Flask(__name__)
CORS(app)

# Register all blueprints
app.register_blueprint(user_bp)
app.register_blueprint(sport_bp)
app.register_blueprint(event_bp)
app.register_blueprint(field_bp)

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

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    logger.info(f"Starting ML Service on port {port}")
    app.run(debug=True, port=port, host='0.0.0.0')
