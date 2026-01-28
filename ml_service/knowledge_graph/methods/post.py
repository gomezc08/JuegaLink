from ..connector import Connector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class Post:
    def __init__(self):
        self.connector = Connector()
    
    def create_post(self, title:str, content:str, event_name_mention:str):
        """Create a new post in Neo4j database. Returns post data."""
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
                user_username_mentions: $user_username_mentions
            })
            RETURN p
            """
            params = {
                "title": title,
                "content": content,
                "event_name_mention": event_name_mention,
                "field_name_mention": field_name_mention,
                "sport_name_mention": sport_name_mention,
                "user_username_mentions": user_username_mentions
            }

            logger.info(f"<post> Adding post to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                post_data = dict(result[0]['p'])
                logger.info(f"<post> Post added to Neo4j DB: {post_data}")
                return post_data
        except Exception as e:
            logger.error(f"<post> Error adding post to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def _get_user_username_mentions(self, event_name_mention:str):
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