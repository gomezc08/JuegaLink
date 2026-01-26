from ..connector import Connector
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)
class User:
    def __init__(self):
        self.connector = Connector()

    def user_signup(self, username: str, email: str, password: str):
        """Create a new user in Neo4j database. Returns user data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(u:User {
                username: $username, 
                email: $email,
                password: $password,
                created_at: $created_at,
                updated_at: $updated_at
            })
            RETURN u
            """
            now = datetime.now().isoformat()
            params = {
                "username": username,
                "email": email,
                "password": password,
                "created_at": now,
                "updated_at": now
            }

            logger.info(f"<user> Adding user to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                user_data = dict(result[0]['u'])
                logger.info(f"<user> User added to Neo4j DB: {user_data}")
                return user_data
            return None
        except Exception as e:
            logger.error(f"<user> Error adding user to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def user_login(self, username: str, password: str):
        """Find a user by username. Returns user data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            # check if user exists and password is correct
            query = """
            MATCH(u:User {username: $username, password: $password})
            RETURN u
            """
            params = {"username": username, "password": password}

            logger.info(f"<user> Searching for user in Neo4j DB and checking password: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                # check if password is correct
                if result[0]['u']['password'] == password:
                    user_data = dict(result[0]['u'])
                    logger.info(f"<user> User found in Neo4j DB and password is correct: {user_data}")
                    return user_data
                else:
                    logger.info(f"<user> User found in Neo4j DB but password is incorrect: {username}")
                    return None
        except Exception as e:
            logger.error(f"<user> Error searching for user in Neo4j DB and checking password: {e}")
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

            logger.info(f"<user> Updating user in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            if result:
                user_data = dict(result[0]['u'])
                logger.info(f"<user> User updated in Neo4j DB: {user_data}")
                return user_data
            return None
        except Exception as e:
            logger.error(f"<user> Error updating user in Neo4j DB: {e}")
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

            logger.info(f"<user> Deleting user from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            success = summary.counters.nodes_deleted > 0
            if success:
                logger.info(f"<user> User deleted from Neo4j DB: {username}")
            else:
                logger.info(f"<user> User not found for deletion in Neo4j DB: {username}")
            return success
        except Exception as e:
            logger.error(f"<user> Error deleting user from Neo4j DB: {e}")
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

            logger.info(f"<user> Adding friend relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> Friend relationship added in Neo4j DB: {user_username} -> {friend_username}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding friend relationship in Neo4j DB: {e}")
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

            logger.info(f"<user> Removing friend relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_deleted > 0
            if success:
                logger.info(f"<user> Friend relationship removed from Neo4j DB: {user_username} -X-> {friend_username}")
            else:
                logger.info(f"<user> Friend relationship not found in Neo4j DB: {user_username} -> {friend_username}")
            return success
        except Exception as e:
            logger.error(f"<user> Error removing friend relationship in Neo4j DB: {e}")
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

            logger.info(f"<user> Getting friends for user in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            friends = [record['friend_username'] for record in result]
            logger.info(f"<user> Found {len(friends)} friends for user in Neo4j DB: {username}")
            return friends
        except Exception as e:
            logger.error(f"<user> Error getting friends for user in Neo4j DB: {e}")
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

            logger.info("<user> Getting all users from Neo4j DB")

            result, summary, keys = driver.execute_query(query)
            
            users = [dict(record['u']) for record in result]
            logger.info(f"<user> Found {len(users)} users in Neo4j DB")
            return users
        except Exception as e:
            logger.error(f"<user> Error getting all users from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_user_followers(self, username: str):
        """Get all followers of a user. Returns list of follower usernames."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})-[:FOLLOWS]->(f:User)
            RETURN f.username as follower_username
            """
            params = {"username": username}

            logger.info(f"<user> Getting followers for user in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            followers = [record['follower_username'] for record in result]
            logger.info(f"<user> Found {len(followers)} followers for user in Neo4j DB: {username}")
            return followers
        except Exception as e:
            logger.error(f"<user> Error getting followers for user in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def get_user(self, username: str):
        """Get a user by username. Returns user data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            RETURN u
            """
            params = {"username": username}

            logger.info(f"<user> Getting user from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            if result:
                user_data = dict(result[0]['u'])
                logger.info(f"<user> User found in Neo4j DB: {user_data}")
                return user_data
            else:
                logger.info(f"<user> User not found in Neo4j DB: {username}")
                return None
        except Exception as e:
            logger.error(f"<user> Error getting user from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def search_users(self, query: str):
        """Search for users by username (case-insensitive partial match). Returns list of user dicts."""
        driver = None
        try:
            driver = self.connector.connect()

            query_cypher = """
            MATCH(u:User)
            WHERE toLower(u.username) CONTAINS toLower($query)
            RETURN u
            ORDER BY u.username
            LIMIT 50
            """
            params = {"query": query}

            logger.info(f"<user> Searching for users in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query_cypher, params)
            
            users = [dict(record['u']) for record in result]
            logger.info(f"<user> Found {len(users)} users matching query in Neo4j DB: {query}")
            return users
        except Exception as e:
            logger.error(f"<user> Error searching for users in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def follow_user(self, user_username: str, follow_username: str):
        """Create a FOLLOWS relationship between users. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(a:User {username: $user_username})
            MATCH(b:User {username: $follow_username})
            CREATE(a)-[:FOLLOWS]->(b)
            RETURN a, b
            """
            params = {
                "user_username": user_username,
                "follow_username": follow_username
            }

            logger.info(f"<user> Adding FOLLOWS relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> FOLLOWS relationship added in Neo4j DB: {user_username} -> {follow_username}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding FOLLOWS relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def play_sport(self, username: str, sport_name: str, skill_level: str, years_experience: int):
        """Create a PLAYS relationship between user and sport. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            MATCH(s:Sport {sport_name: $sport_name})
            CREATE(u)-[:PLAYS {
                skill_level: $skill_level,
                years_experience: $years_experience,
                added_at: $added_at
            }]->(s)
            RETURN u, s
            """
            params = {
                "username": username,
                "sport_name": sport_name,
                "skill_level": skill_level,
                "years_experience": years_experience,
                "added_at": datetime.now().isoformat()
            }

            logger.info(f"<user> Adding PLAYS relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> PLAYS relationship added in Neo4j DB: {username} -> {sport_name}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding PLAYS relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def interested_in_sport(self, username: str, sport_name: str):
        """Create an INTERESTED_IN relationship between user and sport. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            MATCH(s:Sport {sport_name: $sport_name})
            CREATE(u)-[:INTERESTED_IN]->(s)
            RETURN u, s
            """
            params = {
                "username": username,
                "sport_name": sport_name
            }

            logger.info(f"<user> Adding INTERESTED_IN relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> INTERESTED_IN relationship added in Neo4j DB: {username} -> {sport_name}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding INTERESTED_IN relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def organize_event(self, username: str, event_name: str):
        """Create an ORGANIZES relationship between user and event. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            MATCH(e:Event {event_name: $event_name})
            CREATE(u)-[:ORGANIZES]->(e)
            RETURN u, e
            """
            params = {
                "username": username,
                "event_name": event_name
            }

            logger.info(f"<user> Adding ORGANIZES relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> ORGANIZES relationship added in Neo4j DB: {username} -> {event_name}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding ORGANIZES relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def attend_event(self, username: str, event_name: str, status: str):
        """Create an ATTENDING relationship between user and event. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            MATCH(e:Event {event_name: $event_name})
            CREATE(u)-[:ATTENDING {status: $status}]->(e)
            RETURN u, e
            """
            params = {
                "username": username,
                "event_name": event_name,
                "status": status
            }

            logger.info(f"<user> Adding ATTENDING relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> ATTENDING relationship added in Neo4j DB: {username} -> {event_name}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding ATTENDING relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def invite_to_event(self, username: str, event_name: str, invited_by: str, status: str = "pending"):
        """Create an INVITED_TO relationship between user and event. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            MATCH(e:Event {event_name: $event_name})
            CREATE(u)-[:INVITED_TO {
                invited_by: $invited_by,
                status: $status
            }]->(e)
            RETURN u, e
            """
            params = {
                "username": username,
                "event_name": event_name,
                "invited_by": invited_by,
                "status": status
            }

            logger.info(f"<user> Adding INVITED_TO relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> INVITED_TO relationship added in Neo4j DB: {username} -> {event_name}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding INVITED_TO relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def favorite_field(self, username: str, field_name: str):
        """Create a FAVORITED relationship between user and field. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(u:User {username: $username})
            MATCH(f:Field {field_name: $field_name})
            CREATE(u)-[:FAVORITED]->(f)
            RETURN u, f
            """
            params = {
                "username": username,
                "field_name": field_name
            }

            logger.info(f"<user> Adding FAVORITED relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<user> FAVORITED relationship added in Neo4j DB: {username} -> {field_name}")
            return success
        except Exception as e:
            logger.error(f"<user> Error adding FAVORITED relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()