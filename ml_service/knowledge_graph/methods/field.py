from ..connector import Connector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class Field:
    def __init__(self):
        self.connector = Connector()

    def create_field(self, field_name: str, address: str):
        """Create a new field in Neo4j database. Returns field data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(f:Field{field_name: $field_name, address: $address})
            RETURN f
            """
            params = {
                "field_name": field_name,
                "address": address
            }

            logger.info(f"<field> Adding field to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                field_data = dict(result[0]['f'])
                logger.info(f"<field> Field added to Neo4j DB: {field_data}")
                return field_data
            return None
        except Exception as e:
            logger.error(f"<field> Error adding field to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_field(self, field_name: str):
        """Get a field by name. Returns field data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(f:Field{field_name: $field_name})
            RETURN f
            """
            params = {
                "field_name": field_name
            }

            logger.info(f"field:Searching for field in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                field_data = dict(result[0]['f'])
                logger.info(f"field:Field found in Neo4j DB: {field_data}")
                return field_data
            logger.info(f"field:Field not found in Neo4j DB: {field_name}")
            return None
        except Exception as e:
            logger.error(f"field:Error searching for field in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_field_by_address(self, address: str):
        """Get a field by address. Returns field data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(f:Field{address: $address})
            RETURN f
            """
            params = {
                "address": address
            }

            logger.info(f"<field> Searching for field by address in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                field_data = dict(result[0]['f'])
                logger.info(f"<field> Field found by address in Neo4j DB: {field_data}")
                return field_data
            logger.info(f"<field> Field not found at address in Neo4j DB: {address}")
            return None
        except Exception as e:
            logger.error(f"<field> Error searching for field by address in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_all_fields(self):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(f:Field)
        RETURN f
        ORDER BY f.field_name
        """

        result, summary, keys = driver.execute_query(query)

        # print result.
        print(f"Found {len(result)} fields:")
        for record in result:
            print(f"  - {record['f']['field_name']} at {record['f']['address']}")

    def delete_field(self, field_name: str, address: str):
        """Delete a field from Neo4j. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(f:Field{field_name: $field_name, address: $address})
            DELETE f
            RETURN f
            """
            params = {
                "field_name": field_name,
                "address": address
            }

            logger.info(f"<field> Deleting field from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            success = summary.counters.nodes_deleted > 0
            if success:
                logger.info(f"<field> Field deleted from Neo4j DB: {field_name} at {address}")
            else:
                logger.info(f"<field> Field not found for deletion in Neo4j DB: {field_name} at {address}")
            return success
        except Exception as e:
            logger.error(f"<field> Error deleting field from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

if __name__ == "__main__":
    queries = Field()
    #queries.create_field("Central Park Field", "123 Main St, New York, NY")
    #queries.get_field("Central Park Field")
    #queries.get_field_by_address("123 Main St, New York, NY")
    #queries.get_all_fields()
    #queries.delete_field("Central Park Field", "123 Main St, New York, NY")
