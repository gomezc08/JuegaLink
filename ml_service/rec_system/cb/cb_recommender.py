"""
Content-based recommendation system.
Uses trainined model to recommend users based on user features.
"""

import os
import pickle
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Set, Dict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from neo4j import GraphDatabase

from feature_engineering import FeatureEngineer

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class CBRecommender:
    def __init__(self):
        model_path = "ml_service/rec_system/data/models/cb_model.pkl"
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.feature_matrix = model_data['feature_matrix']
        self.usernames = model_data['usernames']
        self.feature_names = model_data['feature_names']

        self.username_to_idx = {
            username: idx for idx, username in enumerate(self.usernames)
        }

        self.feature_engineer = FeatureEngineer()

        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        neo4j_database = os.getenv("NEO4J_DATABASE")
        
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        self.database = os.getenv("NEO4J_DATABASE")
        self.session = self.driver.session(database=neo4j_database)
        
        self.feature_matrix = model_data['feature_matrix']
        self.usernames = model_data['usernames']
        self.feature_names = model_data['feature_names']
    
    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
    
    def _session(self):
        """Create a Neo4j session."""
        if not self.driver:
            raise RuntimeError("Neo4j driver not initialized")
        if self.database:
            return self.driver.session(database=self.database)
        return self.driver.session()
    
    def _fetch_user_from_neo4j(self, username: str) -> Optional[Dict]:
        """
        Fetch user data from Neo4j.
        
        Args:
            username: Username to fetch
            
        Returns:
            User data dict or None if not found
        """
        if not self.driver:
            logger.warning("Cannot fetch user - Neo4j not connected")
            return None
        
        query = """
        MATCH (u:User {name: $username})
        RETURN 
            u.name AS username,
            u.age AS age,
            u.sport AS favorite_sport,
            u.competitive_level AS competitive_level,
            u.latitude AS latitude,
            u.longitude AS longitude
        """
        with self._session() as session:
            result = session.run(query, username=username)
            record = result.single()
            
            if not record:
                return None
            
            return {
                'username': record['username'],
                'age': record['age'],
                'favorite_sport': record['favorite_sport'],
                'competitive_level': record['competitive_level'],
                'latitude': record['latitude'],
                'longitude': record['longitude']
            }
    
    def get_user_features(self, username: str) -> Optional[np.ndarray]:
        """
        Get feature vector for a user.
        First checks cached matrix, then falls back to Neo4j + on-the-fly featurization.
        
        Args:
            username: Username to get features for
            
        Returns:
            Feature vector (1D numpy array) or None if user not found
        """
        # Check if user is in cached model
        if username in self.username_to_idx:
            idx = self.username_to_idx[username]
            return self.feature_matrix[idx]
        
        user_data = self._fetch_user_from_neo4j(username)
        if user_data is None:
            logger.warning("User '%s' not found in Neo4j either", username)
            return None
        
        # Featurize on-the-fly
        features = self.feature_engineer.featurize_user(user_data)
        logger.info("Featurized user '%s' on-the-fly", username)
        
        return features
    
    def get_similar_users(
        self,
        username: str,
        k: int = 10,
        exclude_users: Optional[Set[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Find k most similar users based on feature similarity.
        
        Args:
            username: Target user
            k: Number of similar users to return
            exclude_users: Set of usernames to exclude from results
            
        Returns:
            List of (username, similarity_score) tuples, sorted by similarity (descending)
        """
        # Get target user's features
        target_features = self.get_user_features(username)
        if target_features is None:
            logger.warning("User '%s' not found", username)
            return []
        
        # Reshape for sklearn
        target_features = target_features.reshape(1, -1)
        
        # Compute cosine similarity with all cached users
        similarities = cosine_similarity(target_features, self.feature_matrix)[0]
        
        # Get indices sorted by similarity (descending)
        sorted_indices = np.argsort(similarities)[::-1]

        # Build results, filtering as needed
        results = []
        exclude_users = exclude_users or set()
        exclude_users.add(username)  # Always exclude self
        
        for idx in sorted_indices:
            candidate_username = self.usernames[idx]
            
            # Skip if in exclude list
            if candidate_username in exclude_users:
                continue
            
            similarity_score = float(similarities[idx])
            results.append((candidate_username, similarity_score))
            
            # Stop when we have k results
            if len(results) >= k:
                break
        
        return results
    
    def recommend_users(
        self,
        username: str,
        k: int = 10,
        already_following: Optional[Set[str]] = None,
        min_similarity: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        Recommend users to follow based on CB feature similarity.
        
        Args:
            username: User to generate recommendations for
            k: Number of recommendations to return
            already_following: Set of usernames already followed (will be excluded)
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            List of (recommended_username, similarity_score) tuples
        """
        # Get similar users, excluding those already followed
        similar_users = self.get_similar_users(
            username=username,
            k=k * 2,  # Get more than needed in case of filtering
            exclude_users=already_following
        )
        
        # Apply minimum similarity threshold
        filtered = [
            (user, score) for user, score in similar_users
            if score >= min_similarity
        ]
        
        # Return top k
        return filtered[:k]
    
    def batch_recommend(
        self,
        usernames: List[str],
        k: int = 10,
        already_following_dict: Optional[Dict[str, Set[str]]] = None
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Generate recommendations for multiple users efficiently.
        
        Args:
            usernames: List of usernames to generate recommendations for
            k: Number of recommendations per user
            already_following_dict: Dict of {username: set of followed users}
            
        Returns:
            Dict of {username: [(recommended_user, score), ...]}
        """
        already_following_dict = already_following_dict or {}
        
        results = {}
        for username in usernames:
            already_following = already_following_dict.get(username, set())
            recommendations = self.recommend_users(
                username=username,
                k=k,
                already_following=already_following
            )
            results[username] = recommendations
        
        return results

def main():
    """Demo usage of CBRecommender."""
    
    recommender = CBRecommender()

    # Single user demo
    target_user = "carlos_m"  # soccer, advanced, Los Angeles
    already_following = {"maria_g", "james_k", "olivia_k"}

    print(f"\n--- CB recommendations for {target_user} ---\n")
    recommendations = recommender.recommend_users(
        username=target_user,
        k=10,
        already_following=already_following,
        min_similarity=0.0
    )
    for i, (rec_user, score) in enumerate(recommendations, 1):
        print(f"  {i}. {rec_user} ({score:.4f})")

    # Batch demo — users across different sports/locations
    batch_users = ["carlos_m", "emma_s", "mike_r", "jenny_l", "ashley_r"]
    print(f"\n--- Batch recommendations ---")
    batch_results = recommender.batch_recommend(
        usernames=batch_users,
        k=5,
        already_following_dict={
            "carlos_m": {"maria_g", "james_k", "olivia_k"},
            "emma_s": {"alex_p", "rachel_d", "sue_s"},
            "mike_r": {"kevin_l", "patrick_b", "rob_f"},
            "jenny_l": {"james_k", "josh_n", "dan_c"},
            "ashley_r": {"sarah_w", "lauren_d", "jessica_t"},
        }
    )
    for username, recs in batch_results.items():
        print(f"\n  {username}:")
        for i, (rec_user, score) in enumerate(recs, 1):
            print(f"    {i}. {rec_user} ({score:.4f})")

    recommender.close()


if __name__ == "__main__":
    main()
