from .connector import Connector
from langchain_openai import ChatOpenAI
from langchain_classic.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

class RAG:
    def __init__(self):
        load_dotenv()
        self.connector = Connector()
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE")
        )
        self.rag_chain = self.create_rag_chain()
    
    def create_rag_chain(self):
        # define llm.
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # create custom QA prompt that better handles context
        # The context comes as a list of dicts from the Cypher query results
        qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant that answers questions based on the provided context from a Neo4j graph database query.

        The context below contains the DIRECT RESULTS from a Cypher query that was executed to answer the question. The context IS the answer to the question.

        Context (query results):
        {context}

        Question: {question}

        Instructions:
        - The context contains the answer to the question. Extract and present the information clearly.
        - If the context shows usernames, names, or other data, that IS the answer.
        - Format your response naturally, listing the information from the context.
        - If the context is empty [], you may assume the user is asking a question with no answer.

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
    
    def query_rag_chain(self, query:str):
        result = self.rag_chain.invoke({"query": query})
        return result

if __name__ == "__main__":
    rag = RAG()
    result = rag.query_rag_chain("Who are john's friends?")
    print(result)
