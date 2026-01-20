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
            email=data['email'],
            password=data['password']
        )
        
        logger.info(f"<ml_service_run> User created: {user}")
        return jsonify({
            "message": "User created successfully",
            "user": {
                "username" : user['username'],
                "email" : user['email']
            }
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
        
        if user:
            logger.info(f"<ml_service_run> User logged in: {user}")
            return jsonify({
                "message": "User logged in successfully",
                "user": user
            }), 200
        else:
            logger.info(f"<ml_service_run> Login failed for user: {data['username']}")
            return jsonify({
                "error": "Invalid username or password"
            }), 401
    except Exception as e:
        logger.error(f"<ml_service_run> Error logging in user: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@app.route('/search/users', methods=['GET'])
def search_users():
    """Search for users by username"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                "users": [],
                "count": 0
            }), 200
        
        users = user_service.search_users(query)
        return jsonify({
            "users": users,
            "count": len(users)
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error searching users: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)