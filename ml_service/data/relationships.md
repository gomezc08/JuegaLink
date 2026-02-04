# JuegaLink Neo4j Graph Relationships

## Node Types

| Node | Key Properties |
|------|----------------|
| User | username, email, age, city, state, bio |
| Event | event_name, host, description, date_time, max_players, current_players |
| Post | title, content, username, created_at, post_id |
| Sport | sport_name |
| Field | field_name, address |

## All Relationships

### User-to-User
```
(User)-[:FRIEND]->(User)
(User)-[:FOLLOWS]->(User)
```

### User-to-Sport
```
(User)-[:PLAYS {skill_level, years_experience, added_at}]->(Sport)
(User)-[:INTERESTED_IN]->(Sport)
```

### User-to-Event
```
(User)-[:ORGANIZES]->(Event)
(User)-[:ATTENDING {status}]->(Event)
(User)-[:INVITED_TO {invited_by, status}]->(Event)
(User)-[:JOINED]->(Event)
```

### User-to-Field
```
(User)-[:FAVORITED]->(Field)
```

### User-to-Post
```
(User)-[:POSTED]->(Post)
(User)-[:LIKED]->(Post)
(User)-[:COMMENTED {content, created_at}]->(Post)
```

### Event Relationships
```
(Event)-[:HOSTED_AT]->(Field)
(Event)-[:HOSTED_BY]->(User)
(Event)-[:FOR_SPORT {min_skill_level}]->(Sport)
```

### Post Relationships
```
(Post)-[:TAGGED]->(User)
(Post)-[:MENTIONS_USER]->(User)
(Post)-[:ABOUT_EVENT]->(Event)
(Post)-[:ABOUT_FIELD]->(Field)
(Post)-[:ABOUT_SPORT]->(Sport)
```

### Field Relationships
```
(Field)-[:SUPPORTS]->(Sport)
```

## Quick Reference

| Relationship | From | To | Properties |
|--------------|------|-----|------------|
| FRIEND | User | User | - |
| FOLLOWS | User | User | - |
| PLAYS | User | Sport | skill_level, years_experience, added_at |
| INTERESTED_IN | User | Sport | - |
| ORGANIZES | User | Event | - |
| ATTENDING | User | Event | status |
| INVITED_TO | User | Event | invited_by, status |
| JOINED | User | Event | - |
| FAVORITED | User | Field | - |
| POSTED | User | Post | - |
| LIKED | User | Post | - |
| COMMENTED | User | Post | content, created_at |
| HOSTED_AT | Event | Field | - |
| HOSTED_BY | Event | User | - |
| FOR_SPORT | Event | Sport | min_skill_level |
| TAGGED | Post | User | - |
| MENTIONS_USER | Post | User | - |
| ABOUT_EVENT | Post | Event | - |
| ABOUT_FIELD | Post | Field | - |
| ABOUT_SPORT | Post | Sport | - |
| SUPPORTS | Field | Sport | - |
