from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph import User

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

user_service = User()

app = Flask(__name__)
CORS(app)

@app.route('/users/signup', methods=['POST'])
def signup_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create user
        logger.info(f"<ml_service_run> Creating user: {data['username']}")
        user = user_service.user_signup(
            username=data['username'],
            email=data.get('email'),
            password=data['password']
        )
        
        logger.info(f"<ml_service_run> User created: {user}")
        return jsonify({
            "message": "User created successfully",
            "user": user
        }), 201
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/users/login', methods=['POST'])
def login_user():
    """Login a user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Login user
        logger.info(f"<ml_service_run> Logging in user: {data['username']}")
        user = user_service.user_login(
            username=data['username'],
            password=data['password']
        )
        
        logger.info(f"<ml_service_run> User logged in: {user}")
        return jsonify({
            "message": "User logged in successfully",
            "user": user
        }), 201
    except Exception as e:
        logger.error(f"<ml_service_run> Error logging in user: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)