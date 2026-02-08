from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from rec_system.ensemble import HybridRecommender

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

rec = HybridRecommender()

rec_bp = Blueprint('rec', __name__)

# recommend users route.
@rec_bp.route('/recommend/users', methods=['POST'])
def recommend_users():
    """Recommend users for a given username"""
    try:
        data = request.get_json()
        if 'username' not in data:
            return jsonify({"error": "Missing required field: username"}), 400
        username = data['username']
        users = rec.recommend(username=username)
        return jsonify({
            "users": users
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error recommending users: {str(e)}")
        return jsonify({"error": str(e)}), 500