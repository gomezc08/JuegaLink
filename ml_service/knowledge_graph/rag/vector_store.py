"""Vector store module for document embedding and retrieval"""

from typing import List
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.retriever = None

    def create_retriever(self):
        """Create a retriever from the vector store"""
        self.vectorstore = FAISS(embedding=self.embeddings)
        self.retriever = self.vectorstore.as_retriever()
    
    def get_retriever(self):
        """Get the retriever from the vector store"""
        return self.retriever
    
    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve documents from the vector store"""
        if self.retriever is None:
            raise ValueError("Vector store is not initalized.")
        return self.retriever.invoke(query)