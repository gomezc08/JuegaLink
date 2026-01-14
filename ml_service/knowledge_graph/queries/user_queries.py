from ..connector import Connector

class UserQueries:
    def __init__(self):
        self.connector = Connector()

    def user_signup(self, username:str, age:int, city:str, state:str, bio:str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        CREATE(u:User{username: $username, age: $age, city: $city, state: $state, bio: $bio})
        RETURN u
        """
        params = {
            "username": username,
            "age": age,
            "city": city,
            "state": state,
            "bio": bio
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Created {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships.")
        for record in result:
            print(f"Nodes involved: {record['u']['username']}")

    def user_login(self, username:str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(u:User{username: $username})
        RETURN u
        """
        params = {
            "username": username
        }

        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Created {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships.")
        for record in result:
            print(f"Nodes involved: {record['u']['username']}")

    def add_friend(self, user_username:str, friend_username:str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(a:User{username: $user_username})
        MATCH(b:User{username: $friend_username})
        CREATE(a)-[:FRIEND]->(b)
        RETURN a, b
        """
        params = {
            "user_username": user_username,
            "friend_username": friend_username
        }

        # execute query.
        result, summary, keys = driver.execute_query(query, params)
    
        # print result.
        print(f"Created {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships.")
        for record in result:
            print(f"Nodes involved: {record['a']['username']}, {record['b']['username']}")

    def remove_friend(self, user_username:str, friend_username:str):
        # connect to db.
        driver = self.connector.connect()

        # create query.
        query = """
        MATCH(a:User{username: $user_username})-[r:FRIEND]->(b:User{username: $friend_username})
        DELETE r
        RETURN a, b
        """
        params = {
            "user_username": user_username,
            "friend_username": friend_username
        }

        # execute query.
        result, summary, keys = driver.execute_query(query, params)

        # print result.
        print(f"Deleted {summary.counters.nodes_deleted} nodes and {summary.counters.relationships_deleted} relationships.")
        for record in result:
            print(f"Nodes involved: {record['a']['username']}, {record['b']['username']}")

if __name__ == "__main__":
    queries = UserQueries()
    #queries.user_signup("john", 25, "New York", "NY", "I like to code.")
    #queries.user_signup("bubby", 25, "New York", "NY", "I like to code.")
    #queries.add_friend("john", "bubby")
    #queries.remove_friend("john", "bubby")