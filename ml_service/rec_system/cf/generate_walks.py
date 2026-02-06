"""Generate random walks for the CF model. All settings via env vars."""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Env keys (with defaults) for random walk tuning
ENV_NEO4J_URI = "NEO4J_URI"
ENV_NEO4J_USERNAME = "NEO4J_USERNAME"
ENV_NEO4J_PASSWORD = "NEO4J_PASSWORD"
ENV_NEO4J_DATABASE = "NEO4J_DATABASE"
ENV_WALK_LENGTH = "WALK_LENGTH"
ENV_WALKS_PER_NODE = "WALKS_PER_NODE"
ENV_WALK_GRAPH_NAME = "WALK_GRAPH_NAME"
ENV_WALK_OUTPUT_DIR = "WALK_OUTPUT_DIR"
ENV_WALK_RANDOM_SEED = "WALK_RANDOM_SEED"
ENV_WALK_CONCURRENCY = "WALK_CONCURRENCY"


def _int_env(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class RandomWalkGenerator:
    def __init__(self):
        self.url = os.getenv(ENV_NEO4J_URI)
        self.user = os.getenv(ENV_NEO4J_USERNAME)
        self.password = os.getenv(ENV_NEO4J_PASSWORD)
        self.database = os.getenv(ENV_NEO4J_DATABASE) or None
        self.driver = None
        if self.url and self.user and self.password:
            self.driver = GraphDatabase.driver(
                self.url,
                auth=(self.user, self.password),
            )
        else:
            raise ValueError("Missing Neo4j env: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")

    def _session(self):
        if self.database:
            return self.driver.session(database=self.database)
        return self.driver.session()

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def create_graph(self, session, graph_name: str):
        """Drop existing projection if present, then create User/FOLLOWS graph."""
        # failIfMissing: false so we don't error when graph doesn't exist yet
        drop_query = "CALL gds.graph.drop($graphName, false) YIELD graphName RETURN graphName"
        try:
            session.run(drop_query, graphName=graph_name)
        except Exception as e:
            logger.debug("Drop graph (may not exist): %s", e)
        create_query = """
        CALL gds.graph.project(
            $graphName,
            'User',
            'FOLLOWS'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        result = session.run(create_query, graphName=graph_name)
        record = result.single()
        logger.info("Graph created: %s", record)
        return record

    def generate_walks(
        self,
        walk_length: int,
        walks_per_node: int,
        graph_name: str,
        random_seed: int = 42,
        concurrency: int = 4,
    ):
        """Generate random walks; return list of walks (each walk = list of usernames)."""
        walks_query = """
        CALL gds.randomWalk.stream($graphName, {
            walkLength: $walkLength,
            walksPerNode: $walksPerNode,
            randomSeed: $randomSeed,
            concurrency: $concurrency
        })
        YIELD nodeIds
        RETURN nodeIds
        """
        with self._session() as session:
            result = session.run(
                walks_query,
                graphName=graph_name,
                walkLength=walk_length,
                walksPerNode=walks_per_node,
                randomSeed=random_seed,
                concurrency=concurrency,
            )
            raw_walks = [record["nodeIds"] for record in result]

        if not raw_walks:
            logger.warning("No walks generated")
            return []

        # Single batch: map all node IDs -> username (avoids N+1 queries)
        all_ids = set()
        for ids in raw_walks:
            all_ids.update(ids)
        id_list = list(all_ids)
        with self._session() as session:
            map_result = session.run(
                """
                UNWIND $nodeIds AS nodeId
                MATCH (u:User) WHERE id(u) = nodeId
                RETURN nodeId, u.username AS username
                """,
                nodeIds=id_list,
            )
            id_to_username = {r["nodeId"]: r["username"] for r in map_result}

        walks = []
        for node_ids in raw_walks:
            walk_usernames = [id_to_username.get(nid, "") for nid in node_ids]
            if any(walk_usernames):
                walks.append(walk_usernames)
        logger.info("Generated %d random walks", len(walks))
        return walks

    def save_walks(self, walks: list, output_dir: str) -> str:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"random_walks_{timestamp}.txt")
        with open(output_file, "w") as f:
            for walk in walks:
                f.write(" ".join(walk) + "\n")
        logger.info("Saved %d walks to %s", len(walks), output_file)
        return output_file

    def run_pipeline(
        self,
        walk_length: Optional[int] = None,
        walks_per_node: Optional[int] = None,
        graph_name: Optional[str] = None,
        output_dir: Optional[str] = None,
        random_seed: Optional[int] = None,
        concurrency: Optional[int] = None,
    ):
        """Full pipeline: create projection, generate walks, save to file. Uses env for any None."""
        walk_length = walk_length if walk_length is not None else _int_env(ENV_WALK_LENGTH, 80)
        walks_per_node = walks_per_node if walks_per_node is not None else _int_env(ENV_WALKS_PER_NODE, 10)
        graph_name = graph_name or os.getenv(ENV_WALK_GRAPH_NAME, "user-follow-graph")
        output_dir = output_dir or os.getenv(ENV_WALK_OUTPUT_DIR, "data/walks")
        random_seed = random_seed if random_seed is not None else _int_env(ENV_WALK_RANDOM_SEED, 42)
        concurrency = concurrency if concurrency is not None else _int_env(ENV_WALK_CONCURRENCY, 4)

        logger.info("Random walk pipeline: graph=%s walk_length=%s walks_per_node=%s", graph_name, walk_length, walks_per_node)
        try:
            with self._session() as session:
                self.create_graph(session, graph_name)
            walks = self.generate_walks(
                walk_length=walk_length,
                walks_per_node=walks_per_node,
                graph_name=graph_name,
                random_seed=random_seed,
                concurrency=concurrency,
            )
            output_file = self.save_walks(walks, output_dir)
            logger.info("Pipeline complete. Next: train embeddings using %s", output_file)
            return output_file
        finally:
            self.close()

    def main(self):
        self.run_pipeline()


if __name__ == "__main__":
    RandomWalkGenerator().main()