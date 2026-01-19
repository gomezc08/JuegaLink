from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from knowledge_graph import User

load_dotenv()

user_service = User()

app = Flask(__name__)
CORS(app)

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'age', 'city', 'state', 'bio']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create user
        user_service.user_signup(
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
        
        return jsonify({
            "message": "User created successfully",
            "user": user
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)