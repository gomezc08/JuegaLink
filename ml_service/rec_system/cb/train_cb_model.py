"""
Training a content-based recommendation model.
Ran periodically to keep model up-to-date.
"""

import os
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
from dotenv import load_dotenv
from neo4j import GraphDatabase

from rec_system.cb.feature_engineering import FeatureEngineer

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class CBModelTrainer:
    """Train content-based model from Neo4j user data."""
    
    def __init__(self):
        """Initialize Neo4j connection and feature engineer."""
        self.url = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE")

        if not all([self.url, self.user, self.password]):
            raise ValueError("Missing Neo4j env: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
        
        self.driver = GraphDatabase.driver(
            self.url,
            auth=(self.user, self.password)
        )
        
        self.feature_engineer = FeatureEngineer()
        
        self.output_dir = str (
            Path(__file__).resolve().parent.parent / "data" / "models"
        )
    
    def close(self):
        """Close Neo4j driver."""
        if self.driver:
            self.driver.close()
    
    def _session(self):
        """Create a Neo4j session."""
        if self.database:
            return self.driver.session(database=self.database)
        return self.driver.session()
    
    def fetch_users(self) -> List[Dict]:
        """
        Fetch all users from Neo4j Database at runtime.

        Returns:
            List of user dicts.
        """
        query = """
        MATCH (u:User)
        RETURN 
            u.name AS username,
            u.age AS age,
            u.sport AS favorite_sport,
            u.competitive_level AS competitive_level,
            u.latitude AS latitude,
            u.longitude AS longitude
        ORDER BY u.name
        """

        # create a session.
        with self._session() as session:
            result = session.run(query)
            users = []
            for record in result:
                users.append({
                    "username": record["username"],
                    "age": record["age"],
                    "favorite_sport": record["favorite_sport"],
                    "competitive_level": record["competitive_level"],
                    "latitude": record["latitude"],
                    "longitude": record["longitude"]
                })
            return users
    
    def featurize_users(self, users: List[Dict]) -> tuple[np.ndarray, List[str]]:
        """
        Featurizes a list of user dicts into a numpy array and a list of feature names.

        Args:
            users: List of user dicts.

        Returns:
            Tuple of numpy array and list of feature names.
        """
        # extract list of usernames.
        usernames = [user["username"] for user in users]

        # featurize users.
        features = self.feature_engineer.featurize_users_batch(users)

        return features, usernames
    
    def save_model(
        self,
        feature_matrix: np.ndarray,
        usernames: List[str],
        feature_names: List[str]
    ) -> Dict[str, str]:
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
                
        # Save complete model as pickle
        model_data = {
            'feature_matrix': feature_matrix,
            'usernames': usernames,
            'feature_names': feature_names,
            'n_users': len(usernames),
            'n_features': len(feature_names)
        }
        
        model_path = os.path.join(
            self.output_dir, "cb_model.pkl"
        )
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info("Saved CB model to: %s", model_path)
        
        return {'model_path': model_path}
    
    def train_model(self) -> Dict[str, str]:
        """
        Full training pipeline: fetch users, featurize, save model.
        
        Returns:
            Dict with paths to saved model files
        """
        try:
            # featch users.
            users = self.fetch_users()

            # featurize users.
            features, usernames = self.featurize_users(users)

            # save model.
            feature_names = self.feature_engineer.feature_names
            saved_files = self.save_model(features, usernames, feature_names)

            return saved_files
        except Exception as e:
            logger.error(f"<cb> Error training model: {e}")
            raise e
        finally:
            self.close()
    

def main():
    """Main entry point."""
    trainer = CBModelTrainer()
    trainer.train_model()

if __name__ == "__main__":
    main()