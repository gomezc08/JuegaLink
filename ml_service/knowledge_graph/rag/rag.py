"""
RAG entry point. The Flask route /query uses RAGChain from rag_chain.py.
This file provides a simple programmatic interface and optional CLI for testing.
"""
from ml_service.knowledge_graph.rag.rag_chain import RAGChain

def query(username: str, query_text: str, history: list = None):
    """Run a single RAG query. Use this or RAGChain directly."""
    history = history if history is not None else []
    rag = RAGChain(username=username, history=history)
    return rag.query_rag_chain(query_text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        user = sys.argv[1]
        q = " ".join(sys.argv[2:])
        print(query(user, q))
    else:
        print("Usage: python -m knowledge_graph.rag.rag <username> <query>")