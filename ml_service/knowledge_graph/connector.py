from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

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
            logger.info("<connector> Neo4j DB connection established.")
            return driver
        except Exception as e:
            logger.error(f"<connector> Neo4j DB connection failed: {e}")
            raise e