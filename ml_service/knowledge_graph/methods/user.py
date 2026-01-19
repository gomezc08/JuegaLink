from ..connector import Connector
from datetime import datetime

class User:
    def __init__(self):
        self.connector = Connector()

    def user_signup(self, username: str, age: int, city: str, state: str, bio: str, 
                    email: str = None, phone_no: str = None):
        """Create a new user in Neo4j database. Returns user data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(u:User {
                username: $username, 
                age: $age, 
                city: $city, 
                state: $state, 
                bio: $bio,
                email: $email,
                phone_no: $phone_no,
                created_at: $created_at,
                updated_at: $updated_at
            })
            RETURN u
            """
            now = datetime.now().isoformat()
            params = {
                "username": username,
                "age": age,
                "city": city,
                "state": state,
                "bio": bio,
                "email": email,
                "phone_no": phone_no,
                "created_at": now,
                "updated_at": now
            }

            result, summary, keys = driver.execute_query(query, params)

            if result:
                user_data = dict(result[0]['u'])
                return user_data
            return None
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def user_login(self, username: str):
        """Find a user by username. Returns user data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            RETURN u
            """
            params = {"username": username}

            result, summary, keys = driver.execute_query(query, params)

            if result:
                user_data = dict(result[0]['u'])
                return user_data
            return None
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def update_user(self, username: str, age: int = None, city: str = None, 
                    state: str = None, bio: str = None, email: str = None, 
                    phone_no: str = None):
        """Update user information in Neo4j. Returns updated user data."""
        driver = None
        try:
            driver = self.connector.connect()

            updates = []
            params = {"username": username, "updated_at": datetime.now().isoformat()}
            
            if age is not None:
                updates.append("u.age = $age")
                params["age"] = age
            if city is not None:
                updates.append("u.city = $city")
                params["city"] = city
            if state is not None:
                updates.append("u.state = $state")
                params["state"] = state
            if bio is not None:
                updates.append("u.bio = $bio")
                params["bio"] = bio
            if email is not None:
                updates.append("u.email = $email")
                params["email"] = email
            if phone_no is not None:
                updates.append("u.phone_no = $phone_no")
                params["phone_no"] = phone_no
            
            updates.append("u.updated_at = $updated_at")
            
            if len(updates) == 1:  # Only updated_at
                return None

            query = f"""
            MATCH(u:User {{username: $username}})
            SET {', '.join(updates)}
            RETURN u
            """

            result, summary, keys = driver.execute_query(query, params)
            
            if result:
                return dict(result[0]['u'])
            return None
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def delete_user(self, username: str):
        """Delete a user from Neo4j. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            DETACH DELETE u
            RETURN count(u) as deleted_count
            """
            params = {"username": username}

            result, summary, keys = driver.execute_query(query, params)
            
            return summary.counters.nodes_deleted > 0
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def add_friend(self, user_username: str, friend_username: str):
        """Add a friend relationship. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(a:User {username: $user_username})
            MATCH(b:User {username: $friend_username})
            CREATE(a)-[:FRIEND]->(b)
            RETURN a, b
            """
            params = {
                "user_username": user_username,
                "friend_username": friend_username
            }

            result, summary, keys = driver.execute_query(query, params)
            return summary.counters.relationships_created > 0
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def remove_friend(self, user_username: str, friend_username: str):
        """Remove a friend relationship. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(a:User {username: $user_username})-[r:FRIEND]->(b:User {username: $friend_username})
            DELETE r
            RETURN a, b
            """
            params = {
                "user_username": user_username,
                "friend_username": friend_username
            }

            result, summary, keys = driver.execute_query(query, params)
            return summary.counters.relationships_deleted > 0
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def get_friends(self, username: str):
        """Get all friends of a user. Returns list of friend usernames."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})-[:FRIEND]->(f:User)
            RETURN f.username as friend_username
            """
            params = {"username": username}

            result, summary, keys = driver.execute_query(query, params)
            
            return [record['friend_username'] for record in result]
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()

    def get_all_users(self):
        """Get all users. Returns list of user dicts."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User)
            RETURN u
            ORDER BY u.created_at DESC
            """

            result, summary, keys = driver.execute_query(query)
            
            return [dict(record['u']) for record in result]
        except Exception as e:
            raise e
        finally:
            if driver:
                driver.close()