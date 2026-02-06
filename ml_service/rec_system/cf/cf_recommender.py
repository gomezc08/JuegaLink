"""
CF-based recommender using pre-trained Node2Vec embeddings.
Loads cf_embeddings.pkl and provides a recommendation API (similar users, recommend to follow).
"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Set

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

# Default path: ml_service/rec_system/data/embeddings/cf_embeddings.pkl
_DEFAULT_EMBEDDINGS_PATH = str(
    Path(__file__).resolve().parent.parent / "data" / "embeddings" / "cf_embeddings.pkl"
)
ENV_EMBEDDINGS_PATH = "EMBEDDINGS_PATH"

class CFRecommender:
    """Collaborative filtering recommender using Node2Vec embeddings (trained on follow-graph walks)."""

    def __init__(self, embeddings_path: Optional[str] = None):
        """
        Initialize recommender by loading pre-trained embeddings.

        Args:
            embeddings_path: Path to cf_embeddings.pkl. If None, uses EMBEDDINGS_PATH env var
                             or default ml_service/rec_system/data/embeddings/cf_embeddings.pkl.
        """
        if embeddings_path is None:
            embeddings_path = os.getenv(ENV_EMBEDDINGS_PATH) or _DEFAULT_EMBEDDINGS_PATH

        path = Path(embeddings_path)
        if not path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {path}")

        with open(path, "rb") as f:
            raw = pickle.load(f)
        self.embeddings_dict = {k: np.asarray(v, dtype=np.float32) for k, v in raw.items()}

        self.usernames = list(self.embeddings_dict.keys())
        self.embeddings_matrix = np.array(
            [self.embeddings_dict[u] for u in self.usernames],
            dtype=np.float32,
        )
        self.username_to_idx = {u: i for i, u in enumerate(self.usernames)}
    
    def get_embedding(self, username: str) -> Optional[np.ndarray]:
        """Return embedding vector for a user, or None if not in vocab."""
        return self.embeddings_dict.get(username)
    
    def get_similar_users(
        self,
        username: str,
        k: int = 10,
        exclude_users: Optional[Set[str]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Return k most similar users by embedding cosine similarity (descending).
        Target user is always excluded. Optionally exclude additional usernames.
        """
        if username not in self.username_to_idx:
            print(f"User '{username}' not in embeddings")
            return []

        exclude = set(exclude_users or set())
        exclude.add(username)

        target_idx = self.username_to_idx[username]     # grab user's index
        target_emb = self.embeddings_matrix[target_idx].reshape(1, -1)  # grab user's embedding
        similarities = cosine_similarity(target_emb, self.embeddings_matrix)[0]  # calculate similarities
        sorted_indices = np.argsort(similarities)[::-1]     # heap: sort indices by similarity descending

        # grab k most similar users
        results = []
        for idx in sorted_indices:
            candidate = self.usernames[idx]
            if candidate in exclude:
                continue
            results.append((candidate, float(similarities[idx])))
            if len(results) >= k:
                break
        return results
    
    def recommend_users(
        self,
        username: str,
        k: int = 10,
        already_following: Optional[Set[str]] = None,
        min_similarity: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """
        Recommend users to follow: similar users not already followed, above min_similarity.
        Returns up to k (username, similarity_score) pairs, sorted by score descending.
        """
        # grab list of k*2 similar users.
        similar = self.get_similar_users(
            username=username,
            k=k * 2,
            exclude_users=already_following,
        )

        # filter: based on threshold
        filtered = [(u, s) for u, s in similar if s >= min_similarity]
        return filtered[:k]
    
    def batch_recommend(
        self,
        usernames: List[str],
        k: int = 10,
        already_following_dict: Optional[dict] = None,
    ) -> dict:
        """
        Recommendations for multiple users.
        Returns {username: [(recommended_user, score), ...]}.
        already_following_dict: optional {username: set of usernames they follow}.
        """
        already_following_dict = already_following_dict or {}
        return {
            u: self.recommend_users(u, k=k, already_following=already_following_dict.get(u, set()))
            for u in usernames
        }
    
    def explain_recommendation(self, target_user: str, recommended_user: str) -> dict:
        """Return similarity and a short explanation for a (target, recommended) pair."""
        if target_user not in self.username_to_idx:
            return {"error": f"Target user '{target_user}' not found"}
        if recommended_user not in self.username_to_idx:
            return {"error": f"Recommended user '{recommended_user}' not found"}

        target_emb = self.get_embedding(target_user).reshape(1, -1)
        rec_emb = self.get_embedding(recommended_user).reshape(1, -1)
        similarity = float(cosine_similarity(target_emb, rec_emb)[0][0])

        top_similar = self.get_similar_users(target_user, k=50)
        rank = next((i for i, (u, _) in enumerate(top_similar, 1) if u == recommended_user), None)

        return {
            "target_user": target_user,
            "recommended_user": recommended_user,
            "similarity_score": similarity,
            "rank_in_top_similar": rank,
            "explanation": (
                f"Based on graph embeddings, {recommended_user} has similarity {similarity:.3f} "
                f"with {target_user} (similar follow patterns)."
            ),
        }


def main():
    """Demo: load embeddings and print recommendations for a user."""
    recommender = CFRecommender()

    # Single user demo
    target_user = "carlos_m"
    already_following = {"maria_g", "james_k", "olivia_k"}

    print(f"\nCF recommendations for {target_user}\n")
    recs = recommender.recommend_users(
        username=target_user,
        k=10,
        already_following=already_following,
        min_similarity=0.0,
    )
    for i, (user, score) in enumerate(recs, 1):
        print(f"  {i}. {user} ({score:.3f})")
    if recs:
        exp = recommender.explain_recommendation(target_user, recs[0][0])
        print(f"\nExplanation: {exp['explanation']}")

    # Batch demo
    batch_users = ["carlos_m", "emma_s", "mike_r", "jenny_l", "ashley_r"]
    print(f"\n--- Batch recommendations ---")
    batch_recs = recommender.batch_recommend(batch_users, k=5)
    for user, user_recs in batch_recs.items():
        print(f"\n  {user}:")
        for i, (rec, score) in enumerate(user_recs, 1):
            print(f"    {i}. {rec} ({score:.3f})")


if __name__ == "__main__":
    main()