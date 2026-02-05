from pathlib import Path
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
import logging

from langchain_openai import ChatOpenAI

from knowledge_graph.rag import GraphBuilder, State, VectorStore
from knowledge_graph.rag.document_ingestion import DocumentIngestion
from knowledge_graph.rag.rag_chain import RAGChain

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

# Lazy-initialized JuegaLink retriever (vector store over guide docs).
_juegalink_retriever = None


def _get_juegalink_retriever():
    """Build or return the shared JuegaLink retriever (loads guide once)."""
    global _juegalink_retriever
    if _juegalink_retriever is not None:
        logger.info(f"<ml_service_run> Returning cached JuegaLink retriever")
        return _juegalink_retriever
    guide_path = (
        Path(__file__).resolve().parent.parent
        / "rag" / "document_ingestion" / "data" / "juegalink_user_guide.md"
    )
    ingestion = DocumentIngestion(chunk_size=500, chunk_overlap=50)
    docs = ingestion.load_data([str(guide_path)])
    chunks = ingestion.split_documents(docs)
    vs = VectorStore()
    retriever = vs.create_retriever_from_documents(chunks, k=4)
    _juegalink_retriever = retriever
    logger.info(f"<ml_service_run> Created JuegaLink retriever")
    return retriever


@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """Query the RAG (graph-based agent with graph cypher QA, Wikipedia, JuegaLink retriever). Body: { username, query }."""
    try:
        data = request.get_json()

        if 'username' not in data or 'query' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        username = data["username"]
        query_text = data["query"].strip()
        history = _user_histories.setdefault(username, [])

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        retriever = _get_juegalink_retriever()
        builder = GraphBuilder(llm=llm, retriever=retriever, username=username, history=history)
        state = builder.run(query_text)
        # LangGraph may return state as a dict
        answer = (state.get("answer") if isinstance(state, dict) else getattr(state, "answer", None)) or "Could not generate an answer."

        history.append((query_text, answer))
        if len(history) > 10:
            _user_histories[username] = history[-10:]

        logger.info(f"<ml_service_run> RAG query result: {answer[:200]}...")
        return jsonify({
            "message": "RAG query successful",
            "result": answer
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error querying RAG: {str(e)}")
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/graph-cypher-query', methods=['POST'])
def graph_cypher_query():
    """Query the RAG. Body: { username, query }."""
    try:
        data = request.get_json()
        
        if 'username' not in data or 'query' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        username = data["username"]
        # Reuse this user's history so the RAG retains conversation across requests.
        history = _user_histories.setdefault(username, [])
        rag_service = RAGChain(username=username, history=history)
        result = rag_service.query_rag_chain(data["query"], username)
        logger.info(f"<ml_service_run> RAG query result: {result}")
        return jsonify({
            "message": "RAG query successful",
            "result": result
        }), 200
    except Exception as e:
        logger.error(f"<ml_service_run> Error querying RAG: {str(e)}")
        return jsonify({"error": str(e)}), 500