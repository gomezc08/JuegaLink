from ..connector import Connector
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger(__name__)


class Post:
    def __init__(self):
        self.connector = Connector()
    
    def create_post(self, title: str, content: str, event_name_mention: str):
        """Create a new post in Neo4j database. Returns post data (including post_id)."""
        # grab list of username(s) from event.
        user_username_mentions = self._get_user_username_mentions(event_name_mention)

        # grab field_name from event.
        field_name_mention = self._get_field_name_mention(event_name_mention)    

        # grab sport_name from event.
        sport_name_mention = self._get_sport_name_mention(event_name_mention)

        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(p:Post{
                title: $title,
                content: $content,
                created_at: $created_at
            })
            RETURN p, elementId(p) AS post_id
            """
            params = {
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"<post> Adding post to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if not result:
                logger.error(f"<post> Failed to add post to Neo4j DB: {params}")
                return None

            record = result[0]
            post_id = record["post_id"]
            post_data = dict(record["p"])
            post_data["post_id"] = post_id

            # create relationships (tags).
            self._create_about_event(post_id, event_name_mention)
            if field_name_mention:
                self._create_about_field(post_id, field_name_mention)
            if sport_name_mention:
                self._create_about_sport(post_id, sport_name_mention)
            for username in (user_username_mentions or []):
                self._create_mentions_user(post_id, username)

            logger.info(f"<post> Post added to Neo4j DB: {post_data}")
            return post_data
        except Exception as e:
            logger.error(f"<post> Error adding post to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post by Neo4j elementId. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            DETACH DELETE p
            """
            params = {"post_id": post_id}

            logger.info(f"<post> Deleting post from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            success = summary.counters.nodes_deleted > 0
            if success:
                logger.info(f"<post> Post deleted from Neo4j DB: {post_id}")
            else:
                logger.info(f"<post> Post not found for deletion in Neo4j DB: {post_id}")
            return success
        except Exception as e:
            logger.error(f"<post> Error deleting post from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_post(self, post_id: str):
        """Get a post by Neo4j elementId. Returns post data dict (including post_id) or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            RETURN p, elementId(p) AS post_id
            """
            params = {"post_id": post_id}

            logger.info(f"<post> Getting post from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                record = result[0]
                post_data = dict(record["p"])
                post_data["post_id"] = record["post_id"]
                logger.info(f"<post> Post found in Neo4j DB: {post_data}")
                return post_data
            logger.info(f"<post> Post not found in Neo4j DB: {post_id}")
            return None
        except Exception as e:
            logger.error(f"<post> Error getting post from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def update_post(self, post_id: str, title: str = None, content: str = None):
        """Update post title/content. Returns updated post data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            updates = []
            params = {"post_id": post_id}

            if title is not None:
                updates.append("p.title = $title")
                params["title"] = title
            if content is not None:
                updates.append("p.content = $content")
                params["content"] = content

            if len(updates) == 0:
                return None

            query = f"""
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            SET {', '.join(updates)}
            RETURN p, elementId(p) AS post_id
            """

            logger.info(f"<post> Updating post in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                record = result[0]
                post_data = dict(record["p"])
                post_data["post_id"] = record["post_id"]
                logger.info(f"<post> Post updated in Neo4j DB: {post_data}")
                return post_data
            return None
        except Exception as e:
            logger.error(f"<post> Error updating post in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def like_post(self, username: str, post_id: str) -> bool:
        """Create a LIKED relationship between user and post. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (u:User {username: $username})
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            CREATE (u)-[:LIKED]->(p)
            RETURN u, p
            """
            params = {"username": username, "post_id": post_id}

            logger.info(f"<post> Adding LIKED relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> LIKED relationship added in Neo4j DB: {username} -> {post_id}")
            else:
                logger.info(f"<post> Failed to add LIKED relationship in Neo4j DB: {username} -> {post_id}")
            return success
        except Exception as e:
            logger.error(f"<post> Error adding LIKED relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def unlike_post(self, username: str, post_id: str) -> bool:
        """Delete a LIKED relationship between user and post. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (u:User {username: $username})-[r:LIKED]->(p:Post)
            WHERE elementId(p) = $post_id
            DELETE r
            """
            params = {"username": username, "post_id": post_id}

            logger.info(f"<post> Removing LIKED relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_deleted > 0
            if success:
                logger.info(f"<post> LIKED relationship removed from Neo4j DB: {username} -X-> {post_id}")
            else:
                logger.info(f"<post> LIKED relationship not found in Neo4j DB: {username} -> {post_id}")
            return success
        except Exception as e:
            logger.error(f"<post> Error removing LIKED relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def comment_on_post(self, username: str, post_id: int, comment: str) -> bool:
        """Create a COMMENTED relationship between user and post. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (u:User {username: $username})
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            CREATE (u)-[:COMMENTED {
                content: $comment,
                created_at: $created_at
            }]->(p)
            RETURN u, p
            """
            params = {
                "username": username,
                "post_id": post_id,
                "comment": comment,
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"<post> Adding COMMENTED relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> COMMENTED relationship added in Neo4j DB: {username} -> {post_id}")
            else:
                logger.info(f"<post> Failed to add COMMENTED relationship in Neo4j DB: {username} -> {post_id}")
            return success
        except Exception as e:
            logger.error(f"<post> Error adding COMMENTED relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def _get_user_username_mentions(self, event_name_mention: str):
        """Get list of username(s) linked to event via JOINED"""
        driver = None
        try:
            driver = self.connector.connect()

            # Users can be linked via JOINED (event join)
            query = """
            MATCH (u:User)-[:JOINED]->(e:Event {event_name: $event_name})
            RETURN collect(DISTINCT u.username) AS user_username_mentions
            """
            params = {"event_name": event_name_mention}

            logger.info(f"<post> Getting user username mentions from event: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                user_username_mentions = result[0]["user_username_mentions"]
                logger.info(f"<post> User username mentions found in event: {user_username_mentions}")
                return user_username_mentions if user_username_mentions else []
            return []
        except Exception as e:
            logger.error(f"<post> Error getting user username mentions from event: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def _get_field_name_mention(self, event_name_mention:str):
        """Get field_name from event."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event {event_name: $event_name})-[:HOSTED_AT]->(f:Field)
            RETURN f.field_name AS field_name_mention
            """
            params = {"event_name": event_name_mention}
            logger.info(f"<post> Getting field name mentions from event: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                field_name_mention = result[0]['field_name_mention']
                logger.info(f"<post> Field name mentions found in event: {field_name_mention}")
                return field_name_mention
        except Exception as e:
            logger.error(f"<post> Error getting field name mentions from event: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def _get_sport_name_mention(self, event_name_mention:str):
        """Get sport_name from event."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event {event_name: $event_name})-[:FOR_SPORT]->(s:Sport)
            RETURN s.sport_name AS sport_name_mention
            """
            params = {"event_name": event_name_mention}
            logger.info(f"<post> Getting sport name mentions from event: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                sport_name_mention = result[0]["sport_name_mention"]
                logger.info(f"<post> Sport name mentions found in event: {sport_name_mention}")
                return sport_name_mention
        except Exception as e:
            logger.error(f"<post> Error getting sport name mentions from event: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def _create_about_event(self, post_id: str, event_name: str) -> bool:
        """Create (Post)-[:ABOUT]->(Event). Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()
            query = """
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            MATCH (e:Event {event_name: $event_name})
            CREATE (p)-[:ABOUT_EVENT]->(e)
            RETURN p, e
            """
            result, summary, _ = driver.execute_query(query, {"post_id": post_id, "event_name": event_name})
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> ABOUT_EVENT relationship created: post -> {event_name}")
            return success
        except Exception as e:
            logger.error(f"<post> Error creating ABOUT_EVENT relationship: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def _create_about_field(self, post_id: str, field_name: str) -> bool:
        """Create (Post)-[:ABOUT]->(Field). Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()
            query = """
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            MATCH (f:Field {field_name: $field_name})
            CREATE (p)-[:ABOUT_FIELD]->(f)
            RETURN p, f
            """
            result, summary, _ = driver.execute_query(query, {"post_id": post_id, "field_name": field_name})
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> ABOUT_FIELD relationship created: post -> {field_name}")
            return success
        except Exception as e:
            logger.error(f"<post> Error creating ABOUT_FIELD relationship: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def _create_about_sport(self, post_id: str, sport_name: str) -> bool:
        """Create (Post)-[:ABOUT]->(Sport). Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()
            query = """
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            MATCH (s:Sport {sport_name: $sport_name})
            CREATE (p)-[:ABOUT_SPORT]->(s)
            RETURN p, s
            """
            result, summary, _ = driver.execute_query(query, {"post_id": post_id, "sport_name": sport_name})
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> ABOUT_SPORT relationship created: post -> {sport_name}")
            return success
        except Exception as e:
            logger.error(f"<post> Error creating ABOUT_SPORT relationship: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def _create_mentions_user(self, post_id: str, username: str) -> bool:
        """Create (Post)-[:MENTIONS_USER]->(User). Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()
            query = """
            MATCH (p:Post)
            WHERE elementId(p) = $post_id
            MATCH (u:User {username: $username})
            CREATE (p)-[:MENTIONS_USER]->(u)
            RETURN p, u
            """
            result, summary, _ = driver.execute_query(query, {"post_id": post_id, "username": username})
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> MENTIONS_USER relationship created: post -> {username}")
            return success
        except Exception as e:
            logger.error(f"<post> Error creating MENTIONS_USER relationship: {e}")
            raise e
        finally:
            if driver:
                driver.close()