from ..connector import Connector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class Sport:
    def __init__(self):
        self.connector = Connector()

    def create_sport(self, sport_name: str):
        """Create a new sport in Neo4j database. Returns sport data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(s:Sport{sport_name: $sport_name})
            RETURN s
            """
            params = {
                "sport_name": sport_name
            }

            logger.info(f"<sport> Adding sport to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                sport_data = dict(result[0]['s'])
                logger.info(f"<sport> Sport added to Neo4j DB: {sport_data}")
                return sport_data
            return None
        except Exception as e:
            logger.error(f"<sport> Error adding sport to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_sport(self, sport_name: str):
        """Get a sport by name. Returns sport data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(s:Sport{sport_name: $sport_name})
            RETURN s
            """
            params = {
                "sport_name": sport_name
            }

            logger.info(f"<sport> Searching for sport in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                sport_data = dict(result[0]['s'])
                logger.info(f"<sport> Sport found in Neo4j DB: {sport_data}")
                return sport_data
            logger.info(f"<sport> Sport not found in Neo4j DB: {sport_name}")
            return None
        except Exception as e:
            logger.error(f"<sport> Error searching for sport in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_all_sports(self):
        """Get all sports. Returns list of sport dicts."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(s:Sport)
            RETURN s
            ORDER BY s.sport_name
            """

            logger.info("<sport> Getting all sports from Neo4j DB")

            result, summary, keys = driver.execute_query(query)

            sports = [dict(record['s']) for record in result]
            logger.info(f"<sport> Found {len(sports)} sports in Neo4j DB")
            return sports
        except Exception as e:
            logger.error(f"<sport> Error getting all sports from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def update_sport(self, old_sport_name: str, new_sport_name: str):
        """Update sport name in Neo4j. Returns updated sport data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(s:Sport {sport_name: $old_sport_name})
            SET s.sport_name = $new_sport_name
            RETURN s
            """
            params = {
                "old_sport_name": old_sport_name,
                "new_sport_name": new_sport_name
            }

            logger.info(f"<sport> Updating sport in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            if result:
                sport_data = dict(result[0]['s'])
                logger.info(f"<sport> Sport updated in Neo4j DB: {sport_data}")
                return sport_data
            return None
        except Exception as e:
            logger.error(f"<sport> Error updating sport in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def delete_sport(self, sport_name: str):
        """Delete a sport from Neo4j. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(s:Sport{sport_name: $sport_name})
            DELETE s
            RETURN s
            """
            params = {
                "sport_name": sport_name
            }

            logger.info(f"<sport> Deleting sport from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            success = summary.counters.nodes_deleted > 0
            if success:
                logger.info(f"<sport> Sport deleted from Neo4j DB: {sport_name}")
            else:
                logger.info(f"<sport> Sport not found for deletion in Neo4j DB: {sport_name}")
            return success
        except Exception as e:
            logger.error(f"<sport> Error deleting sport from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

if __name__ == "__main__":
    queries = Sport()
    #queries.create_sport("Basketball")
    #queries.create_sport("Soccer")
    #queries.get_sport("Basketball")
    #queries.get_all_sports()
    #queries.delete_sport("Basketball")

