# ML Service API Documentation

This service provides a RESTful API for managing users, sports, events, and fields in the JuegaLink knowledge graph (Neo4j database).

## Running the Service

```bash
python ml_service_run.py
```

The service will start on port 5000 (or the port specified in the `FLASK_PORT` environment variable).

## Base URL

```
http://localhost:5000
```

## API Endpoints

### User Routes

#### Create User (Signup)
- **POST** `/users/signup`
- **Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response:** 201 Created
  ```json
  {
    "message": "User created successfully",
    "user": {
      "username": "string",
      "email": "string"
    }
  }
  ```

#### User Login
- **POST** `/users/login`
- **Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response:** 200 OK or 401 Unauthorized

#### Update User
- **PUT** `/users/update`
- **Body:**
  ```json
  {
    "username": "string",
    "age": integer (optional),
    "city": "string" (optional),
    "state": "string" (optional),
    "bio": "string" (optional),
    "email": "string" (optional),
    "phone_no": "string" (optional)
  }
  ```
- **Response:** 200 OK

#### Delete User
- **DELETE** `/users/delete`
- **Body:**
  ```json
  {
    "username": "string"
  }
  ```
- **Response:** 200 OK

#### User Follow User
- **POST** `/users/follow`
- **Body:**
  ```json
  {
    "username": "string",
    "follow_username": "string"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:FOLLOWS]->(User)

#### User Play Sport
- **POST** `/users/play-sport`
- **Body:**
  ```json
  {
    "username": "string",
    "sport_name": "string",
    "skill_level": "Beginner|Intermediate|Advanced|Competitive",
    "years_experience": integer
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:PLAYS {skill_level, years_experience, added_at}]->(Sport)

#### User Interested in Sport
- **POST** `/users/interested-in-sport`
- **Body:**
  ```json
  {
    "username": "string",
    "sport_name": "string"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:INTERESTED_IN]->(Sport)

#### User Organize Event
- **POST** `/users/organize-event`
- **Body:**
  ```json
  {
    "username": "string",
    "event_name": "string"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:ORGANIZES]->(Event)

#### User Attend Event
- **POST** `/users/attend-event`
- **Body:**
  ```json
  {
    "username": "string",
    "event_name": "string",
    "status": "confirmed|maybe|declined"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:ATTENDING {status}]->(Event)

#### User Invite to Event
- **POST** `/users/invite-to-event`
- **Body:**
  ```json
  {
    "username": "string",
    "event_name": "string",
    "invited_by": "string",
    "status": "pending|accepted|declined" (optional, default: "pending")
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:INVITED_TO {invited_by, status}]->(Event)

#### User Favorite Field
- **POST** `/users/favorite-field`
- **Body:**
  ```json
  {
    "username": "string",
    "field_name": "string"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (User)-[:FAVORITED]->(Field)

---

### Sport Routes

#### Create Sport
- **POST** `/sports/create`
- **Body:**
  ```json
  {
    "sport_name": "string"
  }
  ```
- **Response:** 201 Created

#### Get Sport
- **POST** `/sports/get`
- **Body:**
  ```json
  {
    "sport_name": "string"
  }
  ```
- **Response:** 200 OK

#### Get All Sports
- **GET** `/sports/all`
- **Response:** 200 OK
  ```json
  {
    "message": "Sports retrieved successfully",
    "sports": [...],
    "count": integer
  }
  ```

#### Update Sport
- **PUT** `/sports/update`
- **Body:**
  ```json
  {
    "old_sport_name": "string",
    "new_sport_name": "string"
  }
  ```
- **Response:** 200 OK

#### Delete Sport
- **DELETE** `/sports/delete`
- **Body:**
  ```json
  {
    "sport_name": "string"
  }
  ```
- **Response:** 200 OK

---

### Event Routes

#### Create Event
- **POST** `/events/create`
- **Body:**
  ```json
  {
    "event_name": "string",
    "description": "string",
    "date_time": "string" (ISO format),
    "max_players": integer,
    "current_players": integer (optional, default: 0)
  }
  ```
- **Response:** 201 Created

#### Get Event
- **POST** `/events/get`
- **Body:**
  ```json
  {
    "event_name": "string"
  }
  ```
- **Response:** 200 OK

#### Get All Events
- **GET** `/events/all`
- **Response:** 200 OK
  ```json
  {
    "message": "Events retrieved successfully",
    "events": [...],
    "count": integer
  }
  ```

#### Update Event
- **PUT** `/events/update`
- **Body:**
  ```json
  {
    "event_name": "string",
    "description": "string" (optional),
    "date_time": "string" (optional),
    "max_players": integer (optional),
    "current_players": integer (optional)
  }
  ```
- **Response:** 200 OK

#### Delete Event
- **DELETE** `/events/delete`
- **Body:**
  ```json
  {
    "event_name": "string"
  }
  ```
- **Response:** 200 OK

#### Event Hosted at Field
- **POST** `/events/hosted-at-field`
- **Body:**
  ```json
  {
    "event_name": "string",
    "field_name": "string"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (Event)-[:HOSTED_AT]->(Field)

#### Event For Sport
- **POST** `/events/for-sport`
- **Body:**
  ```json
  {
    "event_name": "string",
    "sport_name": "string",
    "min_skill_level": "Beginner|Intermediate|Advanced|Competitive"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (Event)-[:FOR_SPORT {min_skill_level}]->(Sport)

---

### Field Routes

#### Create Field
- **POST** `/fields/create`
- **Body:**
  ```json
  {
    "field_name": "string",
    "address": "string"
  }
  ```
- **Response:** 201 Created

#### Get Field
- **POST** `/fields/get`
- **Body:**
  ```json
  {
    "field_name": "string"
  }
  ```
- **Response:** 200 OK

#### Get Field by Address
- **POST** `/fields/get-by-address`
- **Body:**
  ```json
  {
    "address": "string"
  }
  ```
- **Response:** 200 OK

#### Get All Fields
- **GET** `/fields/all`
- **Response:** 200 OK
  ```json
  {
    "message": "Fields retrieved successfully",
    "fields": [...],
    "count": integer
  }
  ```

#### Update Field
- **PUT** `/fields/update`
- **Body:**
  ```json
  {
    "field_name": "string",
    "address": "string" (optional),
    "new_field_name": "string" (optional)
  }
  ```
- **Response:** 200 OK

#### Delete Field
- **DELETE** `/fields/delete`
- **Body:**
  ```json
  {
    "field_name": "string",
    "address": "string"
  }
  ```
- **Response:** 200 OK

#### Field Supports Sport
- **POST** `/fields/supports-sport`
- **Body:**
  ```json
  {
    "field_name": "string",
    "sport_name": "string"
  }
  ```
- **Response:** 201 Created
- **Relationship:** (Field)-[:SUPPORTS]->(Sport)

---

### Utility Routes

#### Health Check
- **GET** `/health`
- **Response:** 200 OK
  ```json
  {
    "status": "healthy",
    "service": "ml_service"
  }
  ```

#### API Root
- **GET** `/`
- **Response:** 200 OK
  ```json
  {
    "message": "JuegaLink ML Service API",
    "endpoints": {
      "users": "/users/*",
      "sports": "/sports/*",
      "events": "/events/*",
      "fields": "/fields/*",
      "health": "/health"
    }
  }
  ```

---

## Error Responses

All endpoints may return the following error responses:

- **400 Bad Request:** Missing required fields or invalid input
- **401 Unauthorized:** Invalid credentials (for login)
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

Error response format:
```json
{
  "error": "Error message here"
}
```

---

## Environment Variables

The service requires the following environment variables (typically set in a `.env` file):

- `NEO4J_URI`: Neo4j database URI
- `NEO4J_USERNAME`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `NEO4J_DATABASE`: Neo4j database name
- `FLASK_PORT`: Flask server port (optional, default: 5000)

---

## Knowledge Graph Schema

### Nodes
- **User**: username, email, password, age, city, state, bio, phone_no, created_at, updated_at
- **Sport**: sport_name
- **Event**: event_name, description, date_time, max_players, current_players
- **Field**: field_name, address

### Relationships
- `(User)-[:FOLLOWS]->(User)`
- `(User)-[:PLAYS {skill_level, years_experience, added_at}]->(Sport)`
- `(User)-[:INTERESTED_IN]->(Sport)`
- `(User)-[:ORGANIZES]->(Event)`
- `(User)-[:ATTENDING {status}]->(Event)`
- `(User)-[:INVITED_TO {invited_by, status}]->(Event)`
- `(User)-[:FAVORITED]->(Field)`
- `(Event)-[:HOSTED_AT]->(Field)`
- `(Event)-[:FOR_SPORT {min_skill_level}]->(Sport)`
- `(Field)-[:SUPPORTS]->(Sport)`

---

## Integration with Rails Application

The Rails application can call these endpoints using the `MlApiService` service class located in `backend/app/services/ml_api_service.rb`.

Example usage:
```ruby
# In Rails service
result = MlApiService.signup(
  username: params[:username],
  email: params[:email],
  password: params[:password]
)
```

Make sure the `ML_SERVICE_URL` environment variable is set in your Rails application to point to the Flask service URL (e.g., `http://localhost:5000`).
