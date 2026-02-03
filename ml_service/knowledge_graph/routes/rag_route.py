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

rag_service = RAG()

rag_bp = Blueprint('rag', __name__)

# RAG route.
@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """Query the RAG. Body: { query }."""
    try:
        data = request.get_json()
        query = data['query']
        result = rag_service.query_rag_chain(query)
        logger.info(f"<ml_service_run> RAG query result: {result}")
        return jsonify({
            "message": "RAG query successful",
            "result": result
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error querying RAG: {str(e)}")
        return jsonify({"error": str(e)}), 500