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

# User creates a post.
@post_bp.route('/posts/create', methods=['POST'])
def create_post():
    """Create a new post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'event_name_mention', 'username']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create post
        logger.info(f"<ml_service_run> Creating post: {data['title']}")
        post = post_service.create_post(
            title=data['title'],
            content=data['content'],
            event_name_mention=data['event_name_mention'],
            username=data['username']
        )
        
        logger.info(f"<ml_service_run> Post created: {post}")
        return jsonify({
            "message": "Post created successfully",
            "post": post
        }), 201
    except Exception as e:
        logger.error(f"<ml_service_run> Error creating post: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User deletes a post.
@post_bp.route('/posts/delete', methods=['DELETE'])
def delete_post():
    """Delete a post"""
    try:
        # Accept JSON body; allow parsing even if Content-Type was not set by client
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON with post_id"}), 400

        # Validate required fields
        required_fields = ['post_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Delete post
        logger.info(f"<ml_service_run> Deleting post: {data['post_id']}")
        success = post_service.delete_post(post_id=data['post_id'])
        
        if success:
            logger.info(f"<ml_service_run> Post deleted: {data['post_id']}")
            return jsonify({
                "message": "Post deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "Post not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error deleting post: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User updates a post.
@post_bp.route('/posts/update', methods=['PUT'])
def update_post():
    """Update a post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'post_id' not in data:
            return jsonify({"error": "Missing required field: post_id"}), 400
        
        # Update post
        logger.info(f"<ml_service_run> Updating post: {data['post_id']}")
        post = post_service.update_post(
            post_id=data['post_id'],
            title=data.get('title'),
            content=data.get('content')
        )
        
        if post:
            logger.info(f"<ml_service_run> Post updated: {post}")
            return jsonify({
                "message": "Post updated successfully",
                "post": post
            }), 200
        else:
            return jsonify({
                "error": "Post not found or no updates provided"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error updating post: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User gets a post.
@post_bp.route('/posts/get-by-id', methods=['POST'])
def get_post():
    """Get a post by id"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'post_id' not in data:
            return jsonify({"error": "Missing required field: post_id"}), 400
        
        # Get post
        logger.info(f"<ml_service_run> Getting post: {data['post_id']}")
        post = post_service.get_post(post_id=data['post_id'])
        
        if post:
            logger.info(f"<ml_service_run> Post found: {post}")
            return jsonify({
                "message": "Post found successfully",
                "post": post
            }), 200
        else:
            return jsonify({
                "error": "Post not found"
            }), 404
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting post: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User gets all posts for a user.
@post_bp.route('/posts/get', methods=['POST'])
def get_user_posts():
    """Get User's Posts"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data:
            return jsonify({"error": "Missing required field: username"}), 400
        
        # Get posts
        logger.info(f"<ml_service_run> Getting all posts for user: {data['username']}")
        posts = post_service.get_user_posts(username=data['username'])
        
        if posts:
            logger.info(f"<ml_service_run> Posts found: {posts}")
        else:
            posts = []
        return jsonify({
            "message": "Posts found successfully",
            "posts": posts
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting user posts: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Get posts where user is tagged.
@post_bp.route('/posts/tagged', methods=['POST'])
def get_tagged_posts():
    """Get posts where user is tagged (MENTIONS_USER). Body: { username }."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data or 'username' not in data:
            return jsonify({"error": "Request body must be JSON with username"}), 400

        username = data['username']
        logger.info(f"<ml_service_run> Getting tagged posts for user: {username}")
        posts = post_service.get_tagged_posts(username=username)

        return jsonify({
            "message": "Tagged posts found successfully",
            "posts": posts if posts else [],
            "count": len(posts) if posts else 0
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting tagged posts: {str(e)}")
        return jsonify({"error": str(e)}), 500


# User likes a post.
@post_bp.route('/posts/like', methods=['POST'])
def like_post():
    """Like a post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'post_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        logger.info(f"<ml_service_run> Liking post: {data}")
        success = post_service.like_post(
            username=data['username'],
            post_id=data['post_id']
        )
        
        if success:
            logger.info(f"<ml_service_run> Post liked")
            return jsonify({
                "message": "Post liked successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to like post"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error liking post: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User unlikes a post.
@post_bp.route('/posts/unlike', methods=['POST'])
def unlike_post():
    """Unlike a post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'post_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        logger.info(f"<ml_service_run> Unliking post: {data}")
        success = post_service.unlike_post(
            username=data['username'],
            post_id=data['post_id']
        )
        
        if success:
            logger.info(f"<ml_service_run> Post unliked")
            return jsonify({
                "message": "Post unliked successfully"
            }), 200
        else:
            return jsonify({
                "error": "Failed to unlike post. Relationship may not exist."
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error unliking post: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get comments for a post.
@post_bp.route('/posts/get-comments', methods=['POST'])
def get_post_comments():
    """Get all comments for a post. Body: { post_id }."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data or 'post_id' not in data:
            return jsonify({"error": "Request body must be JSON with post_id"}), 400
        post_id = data['post_id']
        comments = post_service.get_post_comments(post_id=post_id)
        return jsonify({
            "message": "Comments found",
            "comments": comments,
            "count": len(comments)
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error getting post comments: {str(e)}")
        return jsonify({"error": str(e)}), 500


# User comments on a post.
@post_bp.route('/posts/comment', methods=['POST'])
def comment_on_post():
    """Comment on a post"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'post_id', 'comment']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        logger.info(f"<ml_service_run> Commenting on post: {data}")
        success = post_service.comment_on_post(
            username=data['username'],
            post_id=data['post_id'],
            comment=data['comment']
        )
        
        if success:
            logger.info(f"<ml_service_run> Comment added to post")
            return jsonify({
                "message": "Comment added to post successfully"
            }), 201
        else:
            return jsonify({
                "error": "Failed to comment on post"
            }), 400
    except Exception as e:
        logger.error(f"<ml_service_run> Error commenting on post: {str(e)}")
        return jsonify({"error": str(e)}), 500