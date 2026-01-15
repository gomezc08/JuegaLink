from ..connector import Connector

class Sport:
    def __init__(self):
        self.connector = Connector()

    def create_sport(self, sport_name: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        CREATE(s:Sport{sport_name: $sport_name})
        RETURN s
        """
        params = {
            "sport_name": sport_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Created {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships.")
        for record in result:
            print(f"Sport created: {record['s']['sport_name']}")

    def get_sport(self, sport_name: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(s:Sport{sport_name: $sport_name})
        RETURN s
        """
        params = {
            "sport_name": sport_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        if result:
            for record in result:
                print(f"Sport found: {record['s']['sport_name']}")
        else:
            print(f"Sport '{sport_name}' not found.")

    def get_all_sports(self):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(s:Sport)
        RETURN s
        ORDER BY s.sport_name
        """

        result, summary, keys = driver.execute_query(query)

        # print result.
        print(f"Found {len(result)} sports:")
        for record in result:
            print(f"  - {record['s']['sport_name']}")

    def delete_sport(self, sport_name: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(s:Sport{sport_name: $sport_name})
        DELETE s
        RETURN s
        """
        params = {
            "sport_name": sport_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Deleted {summary.counters.nodes_deleted} nodes and {summary.counters.relationships_deleted} relationships.")
        if result:
            print(f"Sport '{sport_name}' deleted.")

if __name__ == "__main__":
    queries = Sport()
    #queries.create_sport("Basketball")
    #queries.create_sport("Soccer")
    #queries.get_sport("Basketball")
    #queries.get_all_sports()
    #queries.delete_sport("Basketball")

