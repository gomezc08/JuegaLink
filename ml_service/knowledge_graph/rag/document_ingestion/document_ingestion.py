""""Document processing module for loading and splitting documents"""

from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from typing import List, Union
from pathlib import Path
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    TextLoader,
    PyPDFDirectoryLoader
)

class DocumentIngestion:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initalize document processor
        Args:
            chunk_size: size of each chunk for our retriever
            chunk_overlap: how many token overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        self.data_path = None
    
    @staticmethod
    def load_pdf(file_path: Union[Path, str]) -> List[Document]:
        """
        Load PDF file
        Args:
            file_path: path to the PDF file
        Returns:
            List of documents
        """
        loader = PyPDFLoader(file_path)
        return loader.load()
    
    @staticmethod
    def load_from_pdf_directory(directory: Union[Path, str]) -> List[Document]:
        """
        Load PDF files from a directory
        Args:
            directory: path to the directory containing the PDF files
        Returns:
            List of documents
        """
        loader = PyPDFDirectoryLoader(directory)
        return loader.load()
    
    @staticmethod
    def load_text(file: Union[Path, str]) -> List[Document]:
        """
        Load text file from either a directory or path.
        Args:
            file: path to the text file
        Returns:
            List of documents
        """
        loader = TextLoader((str(file, encoding="utf-8")))
        return loader.load()
    
    @staticmethod
    def load_web(url: str) -> List[Document]:
        """
        Load data from a URL
        Args:
            url: URL of the web page
        Returns:
            List of documents
        """
        loader = WebBaseLoader(url)
        return loader.load()
    
    @staticmethod
    def load_data(sources: List[str]) -> List[Document]:
        """
        Load documents from URLs, PDFs, and/or text files
        Args:
            sources: List of URLs, PDF folder paths, or text files
        Returns:
            List of loaded documents
        """
        documents = []
        for source in sources:
            # case 1: PDF files.
            if source.endswith(".pdf"):
                documents.extend(DocumentIngestion.load_pdf(source))
            
            # case 2: text files.
            elif source.endswith(".txt"):
                documents.extend(DocumentIngestion.load_text(source))
            
            # case 3: URL.
            elif source.startswith("http//") or source.startswith("https//"):
                documents.extend(DocumentIngestion.load_web(source))
            
            # case 4: unavailable data source.
            else:
                raise ValueError(
                    f"Unsupported source type: {source}. "
                    "Use URL, .txt file, or PDF directory."
                )
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks
        Args:
            documents: List of documents
        Returns:
            List of chunks
        """
        return self.text_splitter.split_documents(documents)
    
    def process_data(self, urls: List[str]):
        """
        Process data from URLs, PDFs, and/or text files
        Args:
            urls: List of URLs, PDF folder paths, or text files
        Returns:
            List of chunks
        """
        documents = self.load_data(urls)
        return self.split_documents(documents)