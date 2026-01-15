from ..connector import Connector

class SkillLevel:
    def __init__(self):
        self.connector = Connector()

    def create_skill_level(self, level_name: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        CREATE(sl:SkillLevel{level_name: $level_name})
        RETURN sl
        """
        params = {
            "level_name": level_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Created {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships.")
        for record in result:
            print(f"Skill level created: {record['sl']['level_name']}")

    def get_skill_level(self, level_name: str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(sl:SkillLevel{level_name: $level_name})
        RETURN sl
        """
        params = {
            "level_name": level_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        if result:
            for record in result:
                print(f"Skill level found: {record['sl']['level_name']}")
        else:
            print(f"Skill level '{level_name}' not found.")

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
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(sl:SkillLevel{level_name: $level_name})
        DELETE sl
        RETURN sl
        """
        params = {
            "level_name": level_name
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Deleted {summary.counters.nodes_deleted} nodes and {summary.counters.relationships_deleted} relationships.")
        if result:
            print(f"Skill level '{level_name}' deleted.")

if __name__ == "__main__":
    queries = SkillLevel()
    #queries.create_skill_level("Beginner")
    #queries.create_skill_level("Intermediate")
    #queries.create_skill_level("Advanced")
    #queries.create_skill_level("Competitive")
    #queries.get_skill_level("Beginner")
    #queries.get_all_skill_levels()
    #queries.delete_skill_level("Beginner")

