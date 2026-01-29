from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph.methods import User

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

user_service = User()

user_bp = Blueprint('users', __name__)

# User routes.
# User signup route.
@user_bp.route('/users/signup', methods=['POST'])
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

# User login/get route.
@user_bp.route('/users/login', methods=['POST'])
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

# User update route.
@user_bp.route('/users/update', methods=['PUT'])
def update_user():
    """Update user information"""
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
                "error": "User not found or no updates provided"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error updating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User delete route.
@user_bp.route('/users/delete', methods=['DELETE'])
def delete_user():
    """Delete a user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data:
            return jsonify({"error": "Missing required field: username"}), 400
        
        # Delete user
        logger.info(f"<ml_service_run> Deleting user: {data['username']}")
        success = user_service.delete_user(username=data['username'])
        
        if success:
            logger.info(f"<ml_service_run> User deleted: {data['username']}")
            return jsonify({
                "message": "User deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "User not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error deleting user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@user_bp.route('/search/users', methods=['GET'])
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

# User follows user route.
@user_bp.route('/users/follow', methods=['POST'])
def follow_user():
    """Create a FOLLOWS relationship between users"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'follow_username']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create FOLLOWS relationship
        logger.info(f"<ml_service_run> Creating FOLLOWS relationship: {data['username']} -> {data['follow_username']}")
        success = user_service.follow_user(
            user_username=data['username'],
            follow_username=data['follow_username']
        )
        
        if success:
            logger.info(f"<ml_service_run> FOLLOWS relationship created")
            return jsonify({
                "message": "User follow relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create follow relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating follow relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User unfollows user route.
@user_bp.route('/users/unfollow', methods=['POST'])
def unfollow_user():
    """Delete a FOLLOWS relationship between users"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'unfollow_username']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Delete FOLLOWS relationship
        logger.info(f"<ml_service_run> Deleting FOLLOWS relationship: {data['username']} -> {data['unfollow_username']}")
        success = user_service.unfollow_user(
            user_username=data['username'],
            unfollow_username=data['unfollow_username']
        )
        
        if success:
            logger.info(f"<ml_service_run> FOLLOWS relationship deleted")
            return jsonify({
                "message": "User unfollow relationship deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "Failed to delete follow relationship. Relationship may not exist."
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error deleting follow relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get user follow requests route.
@user_bp.route('/users/follow_requests', methods=['GET'])
def get_user_follow_requests():
    """Get all follow requests for a user"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({"error": "Missing required field: username"}), 400
        
        # Get user follow requests
        logger.info(f"<ml_service_run> Getting follow requests for user: {username}")
        follow_requests = user_service.get_user_follow_requests(username=username)
        
        if follow_requests:
            logger.info(f"<ml_service_run> Found {len(follow_requests)} follow requests for user: {username}")
            return jsonify({
                "message": "User follow requests retrieved successfully",
                "follow_requests": follow_requests
            }), 200
        else:
            return jsonify({
                "message": "User follow requests retrieved successfully",
                "follow_requests": []
            }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting user follow requests: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get user followers route.
@user_bp.route('/users/followers', methods=['GET'])
def get_user_followers():
    """Get all followers of a user"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({"error": "Missing required field: username"}), 400
        
        # Get user followers
        logger.info(f"<ml_service_run> Getting followers for user: {username}")
        followers = user_service.get_user_followers(username=username)
        
        if followers:
            logger.info(f"<ml_service_run> Found {len(followers)} followers for user: {username}")
            return jsonify({
                "message": "User followers retrieved successfully",
                "followers": followers
            }), 200
        else:
            return jsonify({
                "message": "User followers retrieved successfully",
                "followers": []
            }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting user followers: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get user following route.
@user_bp.route('/users/following', methods=['GET'])
def get_user_following():
    """Get all following of a user"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({"error": "Missing required field: username"}), 400
        
        # Get user following
        logger.info(f"<ml_service_run> Getting following for user: {username}")
        following = user_service.get_user_following(username=username)
        
        if following:
            logger.info(f"<ml_service_run> Found {len(following)} following for user: {username}")
            return jsonify({
                "message": "User following retrieved successfully",
                "following": following
            }), 200
        else:
            return jsonify({
                "message": "User following retrieved successfully",
                "following": []
            }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting user following: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
# User plays sport route.
@user_bp.route('/users/play-sport', methods=['POST'])
def play_sport():
    """Create a PLAYS relationship between user and sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'sport_name', 'skill_level', 'years_experience']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate skill_level
        valid_skill_levels = ["Beginner", "Intermediate", "Advanced", "Competitive"]
        if data['skill_level'] not in valid_skill_levels:
            return jsonify({
                "error": f"Invalid skill_level. Must be one of: {', '.join(valid_skill_levels)}"
            }), 400
        
        # Create PLAYS relationship
        logger.info(f"<ml_service_run> Creating PLAYS relationship: {data['username']} -> {data['sport_name']}")
        success = user_service.play_sport(
            username=data['username'],
            sport_name=data['sport_name'],
            skill_level=data['skill_level'],
            years_experience=data['years_experience']
        )
        
        if success:
            logger.info(f"<ml_service_run> PLAYS relationship created")
            return jsonify({
                "message": "User play sport relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create play sport relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating play sport relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User interested in sport route.
@user_bp.route('/users/interested-in-sport', methods=['POST'])
def interested_in_sport():
    """Create an INTERESTED_IN relationship between user and sport"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'sport_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create INTERESTED_IN relationship
        logger.info(f"<ml_service_run> Creating INTERESTED_IN relationship: {data['username']} -> {data['sport_name']}")
        success = user_service.interested_in_sport(
            username=data['username'],
            sport_name=data['sport_name']
        )
        
        if success:
            logger.info(f"<ml_service_run> INTERESTED_IN relationship created")
            return jsonify({
                "message": "User interested in sport relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create interested in sport relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating interested in sport relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User organizes event route.
@user_bp.route('/users/organize-event', methods=['POST'])
def organize_event():
    """Create an ORGANIZES relationship between user and event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'event_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create ORGANIZES relationship
        logger.info(f"<ml_service_run> Creating ORGANIZES relationship: {data['username']} -> {data['event_name']}")
        success = user_service.organize_event(
            username=data['username'],
            event_name=data['event_name']
        )
        
        if success:
            logger.info(f"<ml_service_run> ORGANIZES relationship created")
            return jsonify({
                "message": "User organize event relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create organize event relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating organize event relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User attending event route.
@user_bp.route('/users/attend-event', methods=['POST'])
def attend_event():
    """Create an ATTENDING relationship between user and event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'event_name', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate status
        valid_statuses = ["confirmed", "maybe", "declined"]
        if data['status'] not in valid_statuses:
            return jsonify({
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }), 400
        
        # Create ATTENDING relationship
        logger.info(f"<ml_service_run> Creating ATTENDING relationship: {data['username']} -> {data['event_name']}")
        success = user_service.attend_event(
            username=data['username'],
            event_name=data['event_name'],
            status=data['status']
        )
        
        if success:
            logger.info(f"<ml_service_run> ATTENDING relationship created")
            return jsonify({
                "message": "User attend event relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create attend event relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating attend event relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User invited to event route.
@user_bp.route('/users/invite-to-event', methods=['POST'])
def invite_to_event():
    """Create an INVITED_TO relationship between user and event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'event_name', 'invited_by']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate status if provided
        status = data.get('status', 'pending')
        valid_statuses = ["pending", "accepted", "declined"]
        if status not in valid_statuses:
            return jsonify({
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }), 400
        
        # Create INVITED_TO relationship
        logger.info(f"<ml_service_run> Creating INVITED_TO relationship: {data['username']} -> {data['event_name']}")
        success = user_service.invite_to_event(
            username=data['username'],
            event_name=data['event_name'],
            invited_by=data['invited_by'],
            status=status
        )
        
        if success:
            logger.info(f"<ml_service_run> INVITED_TO relationship created")
            return jsonify({
                "message": "User invite to event relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create invite to event relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating invite to event relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User favorited field route.
@user_bp.route('/users/favorite-field', methods=['POST'])
def favorite_field():
    """Create a FAVORITED relationship between user and field"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'field_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create FAVORITED relationship
        logger.info(f"<ml_service_run> Creating FAVORITED relationship: {data['username']} -> {data['field_name']}")
        success = user_service.favorite_field(
            username=data['username'],
            field_name=data['field_name']
        )
        
        if success:
            logger.info(f"<ml_service_run> FAVORITED relationship created")
            return jsonify({
                "message": "User favorite field relationship created successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to create favorite field relationship"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating favorite field relationship: {str(e)}")
        return jsonify({"error": str(e)}), 500

# For standalone running
if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(user_bp)
    app.run(debug=True)