import sys
from pathlib import Path
from knowledge_graph.connector import Connector
from langchain_openai import ChatOpenAI
from langchain_classic.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

class RAG:
    # Max (user, assistant) pairs to keep in context so prompts don't grow unbounded.
    MAX_HISTORY_PAIRS = 10

    def __init__(self, username: str, history: list = None):
        load_dotenv()
        self.username = username
        # Use shared history list if provided (for cross-request retention); otherwise in-memory only for this instance.
        self.history = history if history is not None else []
        self.connector = Connector()
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE")
        )
        self.rag_chain = self.create_rag_chain(username)

    def create_rag_chain(self, username: str):
        # define llm.
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # Build history string from self.history; embed in template (chain only passes context/question).
        if self.history:
            history_lines = [
                f"User: {u}\nAssistant: {a}" for u, a in self.history
            ]
            history_block = "Previous conversation:\n" + "\n\n".join(history_lines)
        else:
            history_block = "No previous conversation yet."

        qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant that answers questions based on the provided context from a Neo4j graph database query in a friendly and conversational manner.

        You are talking to """
            + username
            + """.

        """
            + history_block
            + """

        The context below contains the DIRECT RESULTS from a Cypher query that was executed to answer the question. The context IS the answer to the question.

        Context (query results):
        {context}

        Question: {question}

        IMPORTANT: if the question is not related to """ + username + """ (or is information that """ + username + """ should not know), politely decline to answer and ask if there is anything else you can help with.
        
        Instructions:
        - The context contains the answer to the question. Extract and present the information clearly.
        - If the context shows usernames, names, or other data, that IS the answer.
        - Format your response naturally, listing the information from the context.
        - If the context is empty [], you may assume the user is asking a question with no answer.
        - Try to ask follow-up questions after you have answered the question (keep the conversation going and be engaging).

        Answer:"""
        )

        # create chain.
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=self.graph,
            qa_prompt=qa_prompt,
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
        )

        return chain
    
    def query_rag_chain(self, query: str, username: str = None):
        username = username or self.username
        # Refresh chain so the QA prompt includes latest conversation history.
        self.rag_chain = self.create_rag_chain(username)
        # Inject username into the query so the Cypher generator uses it (not a placeholder).
        query_with_user = f"{query} [Current user's username in the database is: {username}]"
        result = self.rag_chain.invoke({"query": query_with_user})
        answer = result.get("result", result)
        self.history.append((query, answer))
        # Keep only last N pairs so context doesn't grow forever.
        if len(self.history) > self.MAX_HISTORY_PAIRS:
            self.history = self.history[-self.MAX_HISTORY_PAIRS :]
        return answer