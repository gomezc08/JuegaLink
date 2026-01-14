from ..connector import Connector

class FieldQueries:
    def __init__(self):
        self.connector = Connector()

    def create_field(self, field_name: str, address: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        CREATE(f:Field{field_name: $field_name, address: $address})
        RETURN f
        """
        params = {
            "field_name": field_name,
            "address": address
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Created {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships.")
        for record in result:
            print(f"Field created: {record['f']['field_name']} at {record['f']['address']}")

    def get_field(self, field_name: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(f:Field{field_name: $field_name})
        RETURN f
        """
        params = {
            "field_name": field_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        if result:
            for record in result:
                print(f"Field found: {record['f']['field_name']} at {record['f']['address']}")
        else:
            print(f"Field '{field_name}' not found.")

    def get_field_by_address(self, address: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(f:Field{address: $address})
        RETURN f
        """
        params = {
            "address": address
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        if result:
            for record in result:
                print(f"Field found: {record['f']['field_name']} at {record['f']['address']}")
        else:
            print(f"Field at address '{address}' not found.")

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
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(f:Field{field_name: $field_name, address: $address})
        DELETE f
        RETURN f
        """
        params = {
            "field_name": field_name,
            "address": address
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Deleted {summary.counters.nodes_deleted} nodes and {summary.counters.relationships_deleted} relationships.")
        if result:
            print(f"Field '{field_name}' at '{address}' deleted.")

if __name__ == "__main__":
    queries = FieldQueries()
    #queries.create_field("Central Park Field", "123 Main St, New York, NY")
    #queries.get_field("Central Park Field")
    #queries.get_field_by_address("123 Main St, New York, NY")
    #queries.get_all_fields()
    #queries.delete_field("Central Park Field", "123 Main St, New York, NY")
