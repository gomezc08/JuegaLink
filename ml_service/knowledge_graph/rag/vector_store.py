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
        """Create an empty retriever (call add_documents or create_retriever_from_documents to populate)."""
        self.vectorstore = FAISS(embedding=self.embeddings)
        self.retriever = self.vectorstore.as_retriever()

    def create_retriever_from_documents(self, documents: List[Document], k: int = 4):
        """Create and set the retriever from a list of documents (e.g. JuegaLink guide chunks)."""
        if not documents:
            self.create_retriever()
            return self.retriever
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        return self.retriever

    def get_retriever(self):
        """Get the retriever from the vector store."""
        return self.retriever

    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve documents from the vector store."""
        if self.retriever is None:
            raise ValueError("Vector store is not initialized.")
        return self.retriever.invoke(query)