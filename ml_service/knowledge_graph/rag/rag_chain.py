import sys
from pathlib import Path
from ml_service.knowledge_graph.connector import Connector
from langchain_openai import ChatOpenAI
from langchain_classic.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

class RAGChain:
    # Max (user, assistant) pairs to keep in context so prompts don't grow unbounded.
    MAX_HISTORY_PAIRS = 10

    def __init__(self, username: str = None, history: list = None):
        load_dotenv()
        self.username = username
        self.history = history if history is not None else []
        self.connector = Connector()
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE")
        )
        # self.rag_chain = self.create_rag_chain(username)
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def create_rag_chain(self, username: str):
        qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant that answers questions based on the provided context from a Neo4j graph database query in a friendly and conversational manner.

            The context below contains the DIRECT RESULTS from a Cypher query that was executed to answer the question. The context IS the answer to the question.

            ## Information
            - User's username: """+ username + """
            - User's question: {question}

            ## Context (query results)
            {context}

            ## Instructions
            - The context contains the answer to the question. Extract and present the information clearly.
            - If the context shows usernames, names, or other data, that IS the answer.
            - Format your response naturally, listing the information from the context and address the user as second person.
            - No raw markdown formatting.
            - Try to ask follow-up questions after you have answered the question (keep the conversation going and be engaging).
            - If the context is empty [], you may assume the user is asking a question with no answer.

            IMPORTANT: if the question is not related to """ + username + """ (violates privacy), politely decline to answer and ask if there is anything else you can help with.

            Answer:"""
        )

        # create chain.
        chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            qa_prompt=qa_prompt,
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
        )

        return chain

    def query_rag_chain(self, query: str, username: str = None, update_history: bool = True):
        username = username or self.username

        # refine query.
        query = self._refine_query(query, username)

        # create RAG chain.
        self.rag_chain = self.create_rag_chain(username)

        # execute rag chain. Chain only accepts "query"; it passes context + question to QA step.
        result = self.rag_chain.invoke({"query": query})
        answer = result.get("result", result)

        if update_history:
            self._add_to_history(query, answer)
        return answer
    
    def _refine_query(self, query: str, username: str = None):
        prompt = PromptTemplate(
            input_variables=["query", "username", "history"],
            template="""
            You are a helpful assistant that refines a user's query to be more specific and clear.

            ## Information
            - Here is the user's query: {query}
            - Here is the current user's username in the database: {username}
            - Here is the previous conversation history: {history}

            ## Instructions
            - Refine the question to be more specific and clear based on the previous conversation history (i.e., replace all pronouns given the history).
            - Make sure to include the current user's username in the query.
            
            ## Output
            Return the refined question as a string.
            """
        )
        chain = prompt | self.llm | StrOutputParser()
        history_str = (
            "\n".join(f"User: {q}\nAssistant: {a}" for q, a in self.history)
            if self.history
            else "None yet."
        )
        result = chain.invoke({"query": query, "username": username, "history": history_str})
        return result
    
    def _add_to_history(self, query: str, answer: str):
        self.history.append((query, answer))
        if len(self.history) > self.MAX_HISTORY_PAIRS:
            self.history = self.history[-self.MAX_HISTORY_PAIRS :]