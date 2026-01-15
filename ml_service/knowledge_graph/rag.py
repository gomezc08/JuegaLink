from .connector import Connector
from langchain_openai import ChatOpenAI
from langchain_classic.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
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

        # create chain.
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=self.graph,
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
        )

        return chain
    
    def query_rag_chain(self, query:str):
        result = self.rag_chain.invoke({"query": query})
        return result

if __name__ == "__main__":
    rag = RAG()
    result = rag.query_rag_chain("Who are John's friends?")
    print(result)
