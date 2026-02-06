"""
Train Node2Vec embeddings using Word2Vec on pre-generated random walks.
All settings via env vars.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from gensim.models import Word2Vec
import pickle

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Env keys for Word2Vec hyperparameters
ENV_VECTOR_SIZE = "VECTOR_SIZE"
ENV_WINDOW = "WINDOW"
ENV_MIN_COUNT = "MIN_COUNT"
ENV_SG = "SG"  # Skip-gram (1) or CBOW (0)
ENV_EPOCHS = "EPOCHS"
ENV_WORKERS = "WORKERS"
ENV_MODELS_OUTPUT_DIR = "MODELS_OUTPUT_DIR"
ENV_EMBEDDINGS_OUTPUT_DIR = "EMBEDDINGS_OUTPUT_DIR"

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DEFAULT_MODELS_OUTPUT_DIR = str(_DATA_DIR / "models")
_DEFAULT_EMBEDDINGS_OUTPUT_DIR = str(_DATA_DIR / "embeddings")

def _int_env(key: str, default: int) -> int:
    """Parse int from env var with fallback."""
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid int for %s='%s', using default %d", key, raw, default)
        return default


class Node2VecTrainer:
    """Train Word2Vec embeddings on random walks (Node2Vec approach)."""

    def __init__(self):
        # Word2Vec hyperparameters from env
        self.vector_size = _int_env(ENV_VECTOR_SIZE, 128)
        self.window = _int_env(ENV_WINDOW, 10)
        self.min_count = _int_env(ENV_MIN_COUNT, 1)
        self.sg = _int_env(ENV_SG, 1)  # 1=skip-gram (Node2Vec uses this)
        self.epochs = _int_env(ENV_EPOCHS, 10)
        self.workers = _int_env(ENV_WORKERS, 4)
        self.models_dir = os.getenv(ENV_MODELS_OUTPUT_DIR, _DEFAULT_MODELS_OUTPUT_DIR)
        self.embeddings_dir = os.getenv(ENV_EMBEDDINGS_OUTPUT_DIR, _DEFAULT_EMBEDDINGS_OUTPUT_DIR)

    def load_walks(self, walks_file: str) -> list:
        """
        Load random walks from file.
        
        Args:
            walks_file: Path to walks file (one walk per line, space-separated usernames)
            
        Returns:
            List of walks, where each walk is a list of usernames
        """
        print("Loading walks from: %s", walks_file)
        
        walks = []
        with open(walks_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    walk = line.split()
                    # Filter out empty usernames (shouldn't happen but safety check)
                    walk = [username for username in walk if username]
                    if walk:
                        walks.append(walk)
        
        print("Loaded %d walks", len(walks))
        
        # Log some stats
        if walks:
            walk_lengths = [len(w) for w in walks]
            avg_length = sum(walk_lengths) / len(walk_lengths)
            print(
                "Walk stats: min=%d, max=%d, avg=%.1f",
                min(walk_lengths),
                max(walk_lengths),
                avg_length,
            )
            
            # Count unique users
            unique_users = set()
            for walk in walks:
                unique_users.update(walk)
            print("Unique users in walks: %d", len(unique_users))
        
        return walks

    def train_word2vec(self, walks: list) -> Word2Vec:
        """
        Train Word2Vec model on walks (this is the Node2Vec embedding step).
        
        Args:
            walks: List of walks (each walk is list of usernames)
            
        Returns:
            Trained Word2Vec model
        """
        print("Training Word2Vec model...")
        print("  vector_size=%d", self.vector_size)
        print("  window=%d", self.window)
        print("  min_count=%d", self.min_count)
        print("  sg=%d (1=skip-gram, 0=CBOW)", self.sg)
        print("  epochs=%d", self.epochs)
        print("  workers=%d", self.workers)
        
        model = Word2Vec(
            sentences=walks,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            sg=self.sg,
            workers=self.workers,
            epochs=self.epochs,
            seed=42,  # Reproducibility
        )
        
        print("✓ Training complete")
        print("  Vocabulary size: %d", len(model.wv))
        
        return model

    def save_model(self, model: Word2Vec, walks_file: str) -> dict:
        """
        Save trained model to models dir and embeddings to embeddings dir.
        Filenames: cf_model.model, cf_embeddings.pkl (no timestamp).
        """
        Path(self.models_dir).mkdir(parents=True, exist_ok=True)
        Path(self.embeddings_dir).mkdir(parents=True, exist_ok=True)

        model_path = os.path.join(self.models_dir, "cf_model.model")
        model.save(model_path)
        print("Saved Word2Vec model to: %s", model_path)

        embeddings_path = os.path.join(self.embeddings_dir, "cf_embeddings.pkl")
        embeddings_dict = {
            username: model.wv[username].tolist()
            for username in model.wv.index_to_key
        }
        with open(embeddings_path, "wb") as f:
            pickle.dump(embeddings_dict, f)
        print("Saved embeddings to: %s", embeddings_path)

        return {
            "model_path": model_path,
            "embeddings_path": embeddings_path,
        }

    def run_pipeline(self, walks_file: str) -> dict:
        """
        Full training pipeline: load walks, train Word2Vec, save model.
        
        Args:
            walks_file: Path to random walks file
            
        Returns:
            Dict with paths to saved model/embeddings
        """
        print("=" * 60)
        print("NODE2VEC TRAINING PIPELINE")
        print("=" * 60)
        
        # Step 1: Load walks
        walks = self.load_walks(walks_file)
        
        if not walks:
            raise ValueError("No walks loaded - cannot train model")
        
        # Step 2: Train Word2Vec (Node2Vec embeddings)
        model = self.train_word2vec(walks)
        
        # Step 3: Save model and embeddings
        saved_files = self.save_model(model, walks_file)
        
        print("=" * 60)
        print("✓ TRAINING COMPLETE")
        print("=" * 60)
        print("Model: %s", saved_files["model_path"])
        print("Embeddings: %s", saved_files["embeddings_path"])
        
        return saved_files


def main():
    """Main execution - looks for most recent walks file or uses env var."""
    # Check if walks file specified in env
    walks_file = os.getenv("WALKS_FILE")
    
    if not walks_file:
        # Auto-detect most recent walks file
        walks_dir = Path(__file__).resolve().parent.parent / "data" / "walks"
        if walks_dir.exists():
            walk_files = sorted(walks_dir.glob("random_walks_*.txt"))
            if walk_files:
                walks_file = str(walk_files[-1])  # Most recent
                print("Auto-detected walks file: %s", walks_file)
            else:
                raise FileNotFoundError(f"No walk files found in {walks_dir}")
        else:
            raise FileNotFoundError(f"Walks directory not found: {walks_dir}")
    
    # Train
    trainer = Node2VecTrainer()
    trainer.run_pipeline(walks_file)


if __name__ == "__main__":
    main()