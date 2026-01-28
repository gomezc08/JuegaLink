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
                event_name_mention: $event_name_mention,
                field_name_mention: $field_name_mention,
                sport_name_mention: $sport_name_mention,
                user_username_mentions: $user_username_mentions,
                created_at: $created_at
            })
            RETURN p, id(p) AS post_id
            """
            params = {
                "title": title,
                "content": content,
                "event_name_mention": event_name_mention,
                "field_name_mention": field_name_mention,
                "sport_name_mention": sport_name_mention,
                "user_username_mentions": user_username_mentions,
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"<post> Adding post to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                record = result[0]
                post_data = dict(record["p"])
                post_data["post_id"] = record["post_id"]
                logger.info(f"<post> Post added to Neo4j DB: {post_data}")
                return post_data
        except Exception as e:
            logger.error(f"<post> Error adding post to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post by internal Neo4j id. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE id(p) = $post_id
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

    def get_post(self, post_id: int):
        """Get a post by internal Neo4j id. Returns post data dict (including post_id) or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE id(p) = $post_id
            RETURN p, id(p) AS post_id
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

    def update_post(self, post_id: int, title: str = None, content: str = None):
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
            WHERE id(p) = $post_id
            SET {', '.join(updates)}
            RETURN p, id(p) AS post_id
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
    
    def like_post(self, username: str, post_id: int) -> bool:
        """Create a LIKED relationship between user and post. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (u:User {username: $username})
            MATCH (p:Post)
            WHERE id(p) = $post_id
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

    def unlike_post(self, username: str, post_id: int) -> bool:
        """Delete a LIKED relationship between user and post. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (u:User {username: $username})-[r:LIKED]->(p:Post)
            WHERE id(p) = $post_id
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
            WHERE id(p) = $post_id
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

    def tag_event(self, post_id: int, event_name: str) -> bool:
        """Tag an event in a post by creating a TAGS_EVENT relationship."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE id(p) = $post_id
            MATCH (e:Event {event_name: $event_name})
            CREATE (p)-[:TAGS_EVENT]->(e)
            RETURN p, e
            """
            params = {"post_id": post_id, "event_name": event_name}

            logger.info(f"<post> Adding TAGS_EVENT relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> TAGS_EVENT relationship added in Neo4j DB: {post_id} -> {event_name}")
            else:
                logger.info(f"<post> Failed to add TAGS_EVENT relationship in Neo4j DB: {post_id} -> {event_name}")
            return success
        except Exception as e:
            logger.error(f"<post> Error adding TAGS_EVENT relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def tag_field(self, post_id: int, field_name: str) -> bool:
        """Tag a field in a post by creating a TAGS_FIELD relationship."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE id(p) = $post_id
            MATCH (f:Field {field_name: $field_name})
            CREATE (p)-[:TAGS_FIELD]->(f)
            RETURN p, f
            """
            params = {"post_id": post_id, "field_name": field_name}

            logger.info(f"<post> Adding TAGS_FIELD relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> TAGS_FIELD relationship added in Neo4j DB: {post_id} -> {field_name}")
            else:
                logger.info(f"<post> Failed to add TAGS_FIELD relationship in Neo4j DB: {post_id} -> {field_name}")
            return success
        except Exception as e:
            logger.error(f"<post> Error adding TAGS_FIELD relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def tag_sport(self, post_id: int, sport_name: str) -> bool:
        """Tag a sport in a post by creating a TAGS_SPORT relationship."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE id(p) = $post_id
            MATCH (s:Sport {sport_name: $sport_name})
            CREATE (p)-[:TAGS_SPORT]->(s)
            RETURN p, s
            """
            params = {"post_id": post_id, "sport_name": sport_name}

            logger.info(f"<post> Adding TAGS_SPORT relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> TAGS_SPORT relationship added in Neo4j DB: {post_id} -> {sport_name}")
            else:
                logger.info(f"<post> Failed to add TAGS_SPORT relationship in Neo4j DB: {post_id} -> {sport_name}")
            return success
        except Exception as e:
            logger.error(f"<post> Error adding TAGS_SPORT relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def tag_user(self, post_id: int, username: str) -> bool:
        """Tag a user in a post by creating a TAGS_USER relationship."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (p:Post)
            WHERE id(p) = $post_id
            MATCH (u:User {username: $username})
            CREATE (p)-[:TAGS_USER]->(u)
            RETURN p, u
            """
            params = {"post_id": post_id, "username": username}

            logger.info(f"<post> Adding TAGS_USER relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<post> TAGS_USER relationship added in Neo4j DB: {post_id} -> {username}")
            else:
                logger.info(f"<post> Failed to add TAGS_USER relationship in Neo4j DB: {post_id} -> {username}")
            return success
        except Exception as e:
            logger.error(f"<post> Error adding TAGS_USER relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def _get_user_username_mentions(self, event_name_mention: str):
        """Get list of username(s) from event."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (u:User)-[:ATTENDING]->(e:Event {event_name: $event_name})
            RETURN collect(u.username) AS user_username_mentions
            """
            params = {"event_name": event_name_mention}

            logger.info(f"<post> Getting user username mentions from event: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                user_username_mentions = result[0]['user_username_mentions']
                logger.info(f"<post> User username mentions found in event: {user_username_mentions}")
                return user_username_mentions
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
                sport_name_mention = result[0]['sport_name_mention']
                logger.info(f"<post> Sport name mentions found in event: {sport_name_mention}")
                return sport_name_mention
        except Exception as e:
            logger.error(f"<post> Error getting sport name mentions from event: {e}")
            raise e
        finally:
            if driver:
                driver.close()