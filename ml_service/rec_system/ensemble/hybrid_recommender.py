"""
Hybrid recommender system.
Uses content-based and collaborative filtering to recommend users.
"""

from rec_system.cb.cb_recommender import CBRecommender
from rec_system.cf.cf_recommender import CFRecommender
from knowledge_graph.methods.user import User
from typing import List, Tuple

class HybridRecommender:
    def __init__(self):
        self.cb_recommender = CBRecommender()
        self.cf_recommender = CFRecommender()
        self.user_methods = User()
        self.cf_weight = 0.5
        self.cb_weight = 0.5
        self.k = 10
        self.follower_threshold = 10
        self.model_name = "weighted"
    
    def _weighted_recommender(self, username: str) -> List[Tuple[str, float]]:
        """
        Recommend users for a given username using a weighted combination of content-based and collaborative filtering.

        Args:
            username: The username of the user to recommend users for.

        Returns:
            A list of tuples of (username, score) sorted by score (descending).
        """
        # grab results from both recommenders.
        cf_result = self.cf_recommender.recommend_users(username=username, k=self.k)
        cb_result = self.cb_recommender.recommend_users(username=username, k=self.k)

        # Convert to dictionaries for easy lookup
        cf_scores = {user: score for user, score in cf_result}
        cb_scores = {user: score for user, score in cb_result}

        # Normalize scores BEFORE combining
        # cf_scores = HybridRecommender._normalize_scores(cf_scores)
        # cb_scores = HybridRecommender._normalize_scores(cb_scores)
        
        # get union of all users.
        all_users = set(cf_scores.keys()) | set(cb_scores.keys())

        # combine results based on weights.
        combined_scores = []
        for user in all_users:
            cf_score = cf_scores.get(user, 0)
            cb_score = cb_scores.get(user, 0)

            # weighted combination of scores.
            combined_score = cf_score * self.cf_weight + cb_score * self.cb_weight
            combined_scores.append((user, combined_score))
        
        # Sort by combined score (descending) and return top-k
        combined_scores.sort(key=lambda x: x[1], reverse=True)
        return combined_scores[:self.k]

    def _switch_recommender(self, username: str) -> List[Tuple[str, float]]:
        """
        Recommend users for a given username using a switch between content-based and collaborative filtering.

        Args:
            username: The username of the user to recommend users for.

        Returns:
            A list of tuples of (username, score) sorted by score (descending).
        """
        # grab number of followers from the user.
        number_of_followers = self.user_methods.get_number_of_followers(username=username)
        if number_of_followers >= self.follower_threshold:
            print(f"Using collaborative filtering for user: {username}")
            return self.cf_recommender.recommend_users(username=username, k=self.k)

        print(f"Using content-based filtering for user: {username}")
        return self.cb_recommender.recommend_users(username=username, k=self.k)
    
    def recommend(self, username: str) -> List[Tuple[str, float]]:
        """
        Recommend users for a given username.
        Args:
            username: The username of the user to recommend users for.

        Returns:
            A list of tuples of (username, score) sorted by score (descending).
        """
        if self.model_name == "weighted":
            return self._weighted_recommender(username=username)
        elif self.model_name == "switched":
            return self._switch_recommender(username=username)
        else:
            raise ValueError(f"Invalid model name: {self.model_name}")
    
    @staticmethod
    def _normalize_scores(scores_dict: dict) -> dict:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        
        Args:
            scores_dict: Dict of {username: score}
            
        Returns:
            Dict of {username: normalized_score}
        """
        if not scores_dict:
            return {}
        
        scores = list(scores_dict.values())
        min_score = min(scores)
        max_score = max(scores)
        
        # Handle edge case: all scores are the same
        if max_score == min_score:
            return {user: 1.0 for user in scores_dict}
        
        # Min-max normalization
        normalized = {
            user: (score - min_score) / (max_score - min_score)
            for user, score in scores_dict.items()
        }
        
        return normalized

if __name__ == "__main__":
    hybrid_recommender = HybridRecommender()
    print(f"Weighted recommender:\n {hybrid_recommender._weighted_recommender(username='carlos_m')}\n\n")
    print(f"Switch recommender:\n {hybrid_recommender._switch_recommender(username='carlos_m')}")