from ..connector import Connector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class Event:
    def __init__(self):
        self.connector = Connector()

    def create_event(self, event_name: str, description: str, date_time: str, max_players: int, current_players: int = 0):
        """Create a new event in Neo4j database. Returns event data."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            CREATE(e:Event{
                event_name: $event_name, 
                description: $description, 
                date_time: $date_time, 
                max_players: $max_players, 
                current_players: $current_players
            })
            RETURN e
            """
            params = {
                "event_name": event_name,
                "description": description,
                "date_time": date_time,
                "max_players": max_players,
                "current_players": current_players
            }

            logger.info(f"<event> Adding event to Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                event_data = dict(result[0]['e'])
                logger.info(f"<event> Event added to Neo4j DB: {event_data}")
                return event_data
            return None
        except Exception as e:
            logger.error(f"<event> Error adding event to Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_event(self, event_name: str):
        """Get an event by name. Returns event data dict or None."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event{event_name: $event_name})
            RETURN e
            """
            params = {
                "event_name": event_name
            }

            logger.info(f"<event> Searching for event in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            if result:
                event_data = dict(result[0]['e'])
                logger.info(f"<event> Event found in Neo4j DB: {event_data}")
                return event_data
            logger.info(f"<event> Event not found in Neo4j DB: {event_name}")
            return None
        except Exception as e:
            logger.error(f"<event> Error searching for event in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def get_all_events(self):
        """Get all events. Returns list of event dicts."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event)
            RETURN e
            ORDER BY e.date_time
            """

            logger.info("<event> Getting all events from Neo4j DB")

            result, summary, keys = driver.execute_query(query)

            events = [dict(record['e']) for record in result]
            logger.info(f"<event> Found {len(events)} events in Neo4j DB")
            return events
        except Exception as e:
            logger.error(f"<event> Error getting all events from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def update_event(self, event_name: str, description: str = None, date_time: str = None, 
                     max_players: int = None, current_players: int = None):
        """Update event information in Neo4j. Returns updated event data."""
        driver = None
        try:
            driver = self.connector.connect()

            updates = []
            params = {"event_name": event_name}
            
            if description is not None:
                updates.append("e.description = $description")
                params["description"] = description
            if date_time is not None:
                updates.append("e.date_time = $date_time")
                params["date_time"] = date_time
            if max_players is not None:
                updates.append("e.max_players = $max_players")
                params["max_players"] = max_players
            if current_players is not None:
                updates.append("e.current_players = $current_players")
                params["current_players"] = current_players
            
            if len(updates) == 0:
                return None

            query = f"""
            MATCH(e:Event {{event_name: $event_name}})
            SET {', '.join(updates)}
            RETURN e
            """

            logger.info(f"<event> Updating event in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            
            if result:
                event_data = dict(result[0]['e'])
                logger.info(f"<event> Event updated in Neo4j DB: {event_data}")
                return event_data
            return None
        except Exception as e:
            logger.error(f"<event> Error updating event in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def delete_event(self, event_name: str):
        """Delete an event from Neo4j. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event{event_name: $event_name})
            DELETE e
            RETURN e
            """
            params = {
                "event_name": event_name
            }

            logger.info(f"<event> Deleting event from Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)

            success = summary.counters.nodes_deleted > 0
            if success:
                logger.info(f"<event> Event deleted from Neo4j DB: {event_name}")
            else:
                logger.info(f"<event> Event not found for deletion in Neo4j DB: {event_name}")
            return success
        except Exception as e:
            logger.error(f"<event> Error deleting event from Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def hosted_at_field(self, event_name: str, field_name: str):
        """Create a HOSTED_AT relationship between event and field. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event {event_name: $event_name})
            MATCH(f:Field {field_name: $field_name})
            CREATE(e)-[:HOSTED_AT]->(f)
            RETURN e, f
            """
            params = {
                "event_name": event_name,
                "field_name": field_name
            }

            logger.info(f"<event> Adding HOSTED_AT relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<event> HOSTED_AT relationship added in Neo4j DB: {event_name} -> {field_name}")
            return success
        except Exception as e:
            logger.error(f"<event> Error adding HOSTED_AT relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()

    def for_sport(self, event_name: str, sport_name: str, min_skill_level: str):
        """Create a FOR_SPORT relationship between event and sport. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH(e:Event {event_name: $event_name})
            MATCH(s:Sport {sport_name: $sport_name})
            CREATE(e)-[:FOR_SPORT {min_skill_level: $min_skill_level}]->(s)
            RETURN e, s
            """
            params = {
                "event_name": event_name,
                "sport_name": sport_name,
                "min_skill_level": min_skill_level
            }

            logger.info(f"<event> Adding FOR_SPORT relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<event> FOR_SPORT relationship added in Neo4j DB: {event_name} -> {sport_name}")
            return success
        except Exception as e:
            logger.error(f"<event> Error adding FOR_SPORT relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()
    
    def user_joined_event(self, event_name: str, username: str):
        """Create a JOINED relationship between a user and an event. Returns True if successful."""
        driver = None
        try:
            driver = self.connector.connect()

            query = """
            MATCH (e:Event {event_name: $event_name})
            MATCH (u:User {username: $username})
            CREATE (u)-[:JOINED]->(e)
            RETURN e, u
            """
            params = {
                "event_name": event_name,
                "username": username,
            }

            logger.info(f"<event> Adding JOINED relationship in Neo4j DB: {params}")

            result, summary, keys = driver.execute_query(query, params)
            success = summary.counters.relationships_created > 0
            if success:
                logger.info(f"<event> JOINED relationship added in Neo4j DB: {username} -> {event_name}")
            else:
                logger.info(f"<event> Join failed (event or user not found): {username} -> {event_name}")
            return success
        except Exception as e:
            logger.error(f"<event> Error adding JOINED relationship in Neo4j DB: {e}")
            raise e
        finally:
            if driver:
                driver.close()