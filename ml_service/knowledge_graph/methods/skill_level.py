from ..connector import Connector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class SkillLevel:
    def __init__(self):
        self.connector = Connector()

    def create_skill_level(self, level_name: str):
        """Create a new skill level in Neo4j database. Returns skill level data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(sl:SkillLevel{level_name: $level_name})
            RETURN sl
            """
            params = {
                "level_name": level_name
            }

            logger.info(f"<skill_level> Adding skill level to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                skill_level_data = dict(result[0]['sl'])
                logger.info(f"<skill_level> Skill level added to Neo4j DB: {skill_level_data}")
                return skill_level_data
            return None
        except Exception as e:
            logger.error(f"<skill_level> Error adding skill level to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_skill_level(self, level_name: str):
        """Get a skill level by name. Returns skill level data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(sl:SkillLevel{level_name: $level_name})
            RETURN sl
            """
            params = {
                "level_name": level_name
            }

            logger.info(f"<skill_level> Searching for skill level in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                skill_level_data = dict(result[0]['sl'])
                logger.info(f"<skill_level> Skill level found in Neo4j DB: {skill_level_data}")
                return skill_level_data
            logger.info(f"<skill_level> Skill level not found in Neo4j DB: {level_name}")
            return None
        except Exception as e:
            logger.error(f"<skill_level> Error searching for skill level in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_all_skill_levels(self):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(sl:SkillLevel)
        RETURN sl
        ORDER BY sl.level_name
        """

        result, summary, keys = driver.execute_query(query)

        # print result.
        print(f"Found {len(result)} skill levels:")
        for record in result:
            print(f"  - {record['sl']['level_name']}")

    def delete_skill_level(self, level_name: str):
        """Delete a skill level from Neo4j. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(sl:SkillLevel{level_name: $level_name})
            DELETE sl
            RETURN sl
            """
            params = {
                "level_name": level_name
            }

            logger.info(f"<skill_level> Deleting skill level from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            success = summary.counters.nodes_deleted > 0
            if success:
                logger.info(f"<skill_level> Skill level deleted from Neo4j DB: {level_name}")
            else:
                logger.info(f"<skill_level> Skill level not found for deletion in Neo4j DB: {level_name}")
            return success
        except Exception as e:
            logger.error(f"<skill_level> Error deleting skill level from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

if __name__ == "__main__":
    queries = SkillLevel()
    #queries.create_skill_level("Beginner")
    #queries.create_skill_level("Intermediate")
    #queries.create_skill_level("Advanced")
    #queries.create_skill_level("Competitive")
    #queries.get_skill_level("Beginner")
    #queries.get_all_skill_levels()
    #queries.delete_skill_level("Beginner")

