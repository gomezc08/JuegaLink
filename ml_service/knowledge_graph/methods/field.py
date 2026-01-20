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
        """Get all fields. Returns list of field dicts."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(f:Field)
            RETURN f
            ORDER BY f.field_name
            """

            result, summary, keys = driver.execute_query(query)
            
            fields = [dict(record['f']) for record in result]
            logger.info(f"<field> Found {len(fields)} fields in Neo4j DB")
            return fields
        except Exception as e:
            logger.error(f"<field> Error getting all fields from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def search_fields(self, query: str):
        """Search for fields by name or address (partial match). Returns list of field dicts."""
        driver = None
        try:
            driver = self.connector.connect()

            search_query = """
            MATCH(f:Field)
            WHERE toLower(f.field_name) CONTAINS toLower($query) 
               OR toLower(f.address) CONTAINS toLower($query)
            RETURN f
            ORDER BY f.field_name
            LIMIT 50
            """
            params = {"query": query}

            logger.info(f"<field> Searching for fields in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(search_query, params)
            
            fields = [dict(record['f']) for record in result]
            logger.info(f"<field> Found {len(fields)} fields matching search in Neo4j DB")
            return fields
        except Exception as e:
            logger.error(f"<field> Error searching for fields in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

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
