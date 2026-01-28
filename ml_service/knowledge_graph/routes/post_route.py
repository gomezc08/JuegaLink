from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph.methods import Post

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

post_service = Post()

post_bp = Blueprint('posts', __name__)

# TODO: User creates a post.
@post_bp.route('/posts/create', methods=['POST'])
def create_post():
    """Create a new post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'event_name_mention']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create post
        logger.info(f"<ml_service_run> Creating post: {data['title']}")
        post = post_service.create_post(
            title=data['title'],
            content=data['content'],
            event_name_mention=data['event_name_mention']
        )
        
        logger.info(f"<ml_service_run> Post created: {post}")
        return jsonify({
            "message": "Post created successfully",
            "post": post
        }), 201
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating post: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
# TODO: User deletes a post.

# TODO: User updates a post.

# TODO: User gets a post.

# TODO: User likes a post.

# TODO: User unlikes a post.

# TODO: User comments on a post.

# TODO: User tags a event in a post.

# TODO: User tags a field in a post.

# TODO: User tags a sport in a post.

# TODO: User tags a user in a post.