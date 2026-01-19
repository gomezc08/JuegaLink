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
        required_fields = ['username', 'age', 'city', 'state', 'bio']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create user
        logger.info(f"<ml_service_run> Creating user: {data['username']}")
        user = user_service.user_signup(
            username=data['username'],
            age=data['age'],
            city=data['city'],
            state=data['state'],
            bio=data['bio'],
            email=data.get('email'),
            phone_no=data.get('phone_no')
        )
        
        # Get the created user to return
        user = user_service.user_login(data['username'])
        logger.info(f"<ml_service_run> User created: {user}")
        return jsonify({
            "message": "User created successfully",
            "user": user
        }), 201
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)