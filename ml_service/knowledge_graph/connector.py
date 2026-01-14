from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

class Connector:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE")
    
    def connect(self):
        try:
            auth = (self.user, self.password)
            driver = GraphDatabase.driver(self.url, auth=auth)
            driver.verify_connectivity()
            print("Connection established.")
            return driver
        except Exception as e:
            print(f"Connection failed: {e}")
            raise e