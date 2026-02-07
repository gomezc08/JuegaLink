"""
Feature engineering for content-based recommendation.
Transforms raw user attributes into feature vectors.
"""

import os
import logging
from typing import Dict, List, Optional
import numpy as np
from pathlib import Path
import json

from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# All possible sports (from your data)
SPORTS = [
    'Soccer', 'Basketball', 'Tennis', 'Baseball', 'Volleyball',
    'American Football', 'Golf', 'Swimming', 'Running', 'Cycling',
    'Hockey', 'Cricket', 'Rugby', 'Badminton', 'Boxing',
    'Martial Arts', 'Skating', 'Skiing', 'Surfing', 'Weightlifting', 'Yoga'
]

# Competitive levels (ordered)
COMPETITIVE_LEVELS = {
    'Beginner': 1,
    'Intermediate': 2,
    'Advanced': 3,
    'Competitive': 4
}

# Age range for normalization
MIN_AGE = 13
MAX_AGE = 100


class FeatureEngineer:
    """Transform raw user attributes into feature vectors."""
    
    def __init__(self, city_coords_path: Optional[str] = None):
        """
        Initialize feature engineer.
        
        Args:
            city_coords_path: Path to JSON file mapping city names to lat/long.
                            If None, will look for default location.
        """
        self.sports = SPORTS
        self.competitive_levels = COMPETITIVE_LEVELS
        
        # Load city coordinates (lat/long mapping)
        self.city_coords = self._load_city_coords(city_coords_path)
        
        # Feature names (for interpretability)
        self.feature_names = self._build_feature_names()
            
    def _load_city_coords(self, city_coords_path: Optional[str]) -> Dict[str, Dict[str, float]]:
        """
        Load city to lat/long mapping from JSON file.
        
        Returns:
            Dict mapping "City, State" -> {"lat": float, "lng": float}
        """
        if city_coords_path is None:
            # Default location
            default_path = Path(__file__).resolve().parent.parent / "data" / "city_coordinates.json"
            city_coords_path = str(default_path)
        
        if not os.path.exists(city_coords_path):
            logger.warning("City coordinates file not found: %s", city_coords_path)
            logger.warning("Geographic features will use (0, 0) for unknown cities")
            return {}
        
        with open(city_coords_path, 'r') as f:
            coords = json.load(f)
        
        logger.info("Loaded coordinates for %d cities", len(coords))
        return coords
    
    def _build_feature_names(self) -> List[str]:
        """Build ordered list of feature names."""
        names = []
        
        # Age feature
        names.append('age_normalized')
        
        # Sport features (one-hot)
        for sport in self.sports:
            names.append(f'sport_{sport.lower().replace(" ", "_")}')
        
        # Competitive level (ordinal)
        names.append('competitive_level')
        
        # Geographic features
        names.append('coordinates')
        
        return names
    
    def _normalize_age(self, age: Optional[int]) -> float:
        """
        Normalize age to [0, 1] range.
        
        Args:
            age: User age
            
        Returns:
            Normalized age between 0 and 1
        """
        if age is None:
            # Default to middle age if missing
            return 0.5
        
        # Clip to valid range
        age = max(MIN_AGE, min(MAX_AGE, age))
        
        # Normalize to [0, 1]
        normalized = (age - MIN_AGE) / (MAX_AGE - MIN_AGE)
        return float(normalized)
    
    def _encode_sport_one_hot(self, favorite_sport: Optional[str]) -> List[float]:
        """
        One-hot encode favorite sport.
        
        Args:
            favorite_sport: User's favorite sport
            
        Returns:
            List of 0s and 1s (length = number of sports)
        """
        encoding = [0.0] * len(self.sports)
        
        if favorite_sport and favorite_sport in self.sports:
            idx = self.sports.index(favorite_sport)
            encoding[idx] = 1.0
        
        return encoding
    
    def _encode_competitive_level(self, level: Optional[str]) -> float:
        """
        Encode competitive level as ordinal value.
        
        Args:
            level: Competitive level string
            
        Returns:
            Normalized ordinal value [0, 1]
        """
        if level is None:
            # Default to intermediate
            return 0.5
        
        # Normalize level string
        level_lower = level.lower().strip()
        
        # Get ordinal value
        ordinal = self.competitive_levels.get(level_lower, 2)  # Default to intermediate
        
        # Normalize to [0, 1]
        max_level = max(self.competitive_levels.values())
        min_level = min(self.competitive_levels.values())
        normalized = (ordinal - min_level) / (max_level - min_level)
        
        return float(normalized)
    
    def _encode_coordinates(self, latitude: float, longitude: float) -> float:
        """
        Encode geographic location as a single float.
        
        Args:
            latitude: Latitude
            longitude: Longitude
        """
        return (latitude + 90) / 180.0  # Normalize to [0, 1]
    
    def featurize_user(self, user_data: Dict) -> np.ndarray:
        """
        Convert raw user data into feature vector.
        
        Args:
            user_data: Dict with keys: username, age, city, state, 
                      favorite_sport, competitive_level, etc.
                      
        Returns:
            Numpy array of features (length = len(feature_names))
        """
        features = []
        
        # Age
        age_norm = self._normalize_age(user_data.get('age'))
        features.append(age_norm)
        
        # Sport (one-hot)
        sport_encoding = self._encode_sport_one_hot(user_data.get('favorite_sport'))
        features.extend(sport_encoding)
        
        # Competitive level
        comp_level = self._encode_competitive_level(user_data.get('competitive_level'))
        features.append(comp_level)
        
        # Geography
        geo_features = self._encode_coordinates(
            user_data.get('latitude'),
            user_data.get('longitude')
        )
        features.append(geo_features)
        
        return np.array(features, dtype=np.float32)
    
    def featurize_users_batch(self, users_data: List[Dict]) -> np.ndarray:
        """
        Featurize multiple users at once.
        
        Args:
            users_data: List of user data dicts
            
        Returns:
            2D numpy array (n_users x n_features)
        """
        feature_vectors = [
            self.featurize_user(user) for user in users_data
        ]
        return np.vstack(feature_vectors)
    
    def get_feature_importance(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """
        Map feature vector back to named features for interpretability.
        
        Args:
            feature_vector: Numpy array of features
            
        Returns:
            Dict mapping feature names to values
        """
        if len(feature_vector) != len(self.feature_names):
            raise ValueError(
                f"Feature vector length {len(feature_vector)} doesn't match "
                f"expected {len(self.feature_names)}"
            )
        
        return {
            name: float(value)
            for name, value in zip(self.feature_names, feature_vector)
        }


def main():
    """Demo usage of FeatureEngineer."""
    
    # Example user data (as it would come from Neo4j)
    example_users = [
        {
            'username': 'chris',
            'age': 28,
            'latitude': 47.6062,
            'longitude': -122.3321,
            'state': 'WA',
            'favorite_sport': 'Soccer',
            'competitive_level': 'competitive'
        },
        {
            'username': 'alice',
            'age': 25,
            'latitude': 45.5231,
            'longitude': -122.6765,
            'state': 'OR',
            'favorite_sport': 'Tennis',
            'competitive_level': 'intermediate'
        },
        {
            'username': 'bob',
            'age': 32,
            'latitude': 47.6062,
            'longitude': -122.3321,
            'state': 'WA',
            'favorite_sport': 'Soccer',
            'competitive_level': 'recreational'
        }
    ]
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    
    print(f"\n{'='*60}")
    print("FEATURE ENGINEERING DEMO")
    print(f"{'='*60}\n")
    
    # Featurize single user
    print("Single user featurization:")
    print(f"User: {example_users[0]['username']}")
    features = engineer.featurize_user(example_users[0])
    print(f"Feature vector shape: {features.shape}")
    print(f"Feature vector: {features}\n")
    
    # Show feature breakdown
    print("Feature breakdown:")
    feature_dict = engineer.get_feature_importance(features)
    for name, value in feature_dict.items():
        if value > 0:  # Only show non-zero features
            print(f"  {name:30s}: {value:.4f}")
    
    # Batch featurization
    print(f"\n{'='*60}")
    print("Batch featurization:")
    batch_features = engineer.featurize_users_batch(example_users)
    print(f"Shape: {batch_features.shape}")
    print(f"(Users: {batch_features.shape[0]}, Features: {batch_features.shape[1]})")
    
    # Compare two users
    print(f"\n{'='*60}")
    print("User similarity (cosine):")
    
    # Chris vs Alice
    sim_chris_alice = cosine_similarity(
        batch_features[0:1], batch_features[1:2]
    )[0][0]
    print(f"  chris <-> alice: {sim_chris_alice:.4f}")
    
    # Chris vs Bob
    sim_chris_bob = cosine_similarity(
        batch_features[0:1], batch_features[2:3]
    )[0][0]
    print(f"  chris <-> bob:   {sim_chris_bob:.4f}")
    
    print(f"\n(Bob and Chris both like Soccer and are in Seattle → higher similarity)")


if __name__ == "__main__":
    main()