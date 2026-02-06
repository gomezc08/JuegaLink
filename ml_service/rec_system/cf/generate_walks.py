"""Generate random walks for the CF model. All settings via env vars.
Falls back to Cypher + in-memory Python walks if GDS is not available.
"""

import os
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError

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

# Default output dir: ml_service/rec_system/data/walks (relative to this file)
_DEFAULT_WALK_OUTPUT_DIR = str(Path(__file__).resolve().parent.parent / "data" / "walks")


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

    def _load_graph_cypher(self) -> dict:
        """Load User-FOLLOWS graph via Cypher. Returns adjacency: username -> [neighbor usernames]."""
        query = """
        MATCH (u:User)-[:FOLLOWS]->(v:User)
        RETURN u.name AS src, v.name AS dst
        """
        with self._session() as session:
            result = session.run(query)
            adj = {}
            for record in result:
                src, dst = record["src"], record["dst"]
                if src and dst:
                    adj.setdefault(src, []).append(dst)
            for record in session.run("MATCH (u:User) RETURN u.name AS username"):
                u = record["username"]
                if u and u not in adj:
                    adj[u] = []
        return adj

    def _walks_python_fallback(
        self,
        walk_length: int,
        walks_per_node: int,
        random_seed: int,
    ) -> list:
        """Generate random walks in Python from Cypher-loaded graph (no GDS)."""
        adjacency = self._load_graph_cypher()
        random.seed(random_seed)
        # Start from nodes that have at least one out-neighbor (so we can extend the walk)
        start_nodes = [u for u, nbrs in adjacency.items() if u and nbrs]
        if not start_nodes:
            # No FOLLOWS edges: emit single-node "walks" so we still have something per user
            all_users = [u for u in adjacency if u]
            if not all_users:
                logger.warning("No User nodes found in graph")
                return []
            logger.warning("No FOLLOWS edges in graph; emitting single-node walks only")
            return [[u] for u in all_users for _ in range(walks_per_node)]
        walks = []
        n_walks = walks_per_node * len(start_nodes)
        for _ in range(n_walks):
            current = random.choice(start_nodes)
            walk = [current]
            for _ in range(walk_length - 1):
                nbrs = adjacency.get(current)
                if not nbrs:
                    break
                current = random.choice(nbrs)
                walk.append(current)
            walks.append(walk)
        logger.info("Generated %d random walks (Cypher fallback, no GDS)", len(walks))
        return walks

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
                RETURN nodeId, u.name AS username
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
        output_dir = output_dir or os.getenv(ENV_WALK_OUTPUT_DIR, _DEFAULT_WALK_OUTPUT_DIR)
        random_seed = random_seed if random_seed is not None else _int_env(ENV_WALK_RANDOM_SEED, 42)
        concurrency = concurrency if concurrency is not None else _int_env(ENV_WALK_CONCURRENCY, 4)

        logger.info("Random walk pipeline: graph=%s walk_length=%s walks_per_node=%s", graph_name, walk_length, walks_per_node)
        try:
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
            except ClientError as e:
                if "ProcedureNotFound" in str(e) or "no procedure" in str(e).lower():
                    logger.info("GDS not available, using Cypher fallback")
                    walks = self._walks_python_fallback(walk_length, walks_per_node, random_seed)
                else:
                    raise
            output_file = self.save_walks(walks, output_dir)
            logger.info("Pipeline complete. Next: train embeddings using %s", output_file)
            return output_file
        finally:
            self.close()

    def main(self):
        self.run_pipeline()


if __name__ == "__main__":
    RandomWalkGenerator().main()