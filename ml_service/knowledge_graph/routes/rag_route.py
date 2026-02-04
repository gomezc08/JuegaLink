from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import os
import logging

from knowledge_graph.rag import RAG

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


rag_bp = Blueprint('rag', __name__)

# Per-user conversation history: username -> list of (user_msg, assistant_msg).
# In-memory; survives across requests for the same process.
_user_histories = {}

# RAG route.
@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """Query the RAG. Body: { username, query }."""
    try:
        data = request.get_json()
        
        if 'username' not in data or 'query' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        username = data["username"]
        # Reuse this user's history so the RAG retains conversation across requests.
        history = _user_histories.setdefault(username, [])
        rag_service = RAG(username=username, history=history)
        result = rag_service.query_rag_chain(data["query"], username)
        logger.info(f"<ml_service_run> RAG query result: {result}")
        return jsonify({
            "message": "RAG query successful",
            "result": result
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error querying RAG: {str(e)}")
        return jsonify({"error": str(e)}), 500