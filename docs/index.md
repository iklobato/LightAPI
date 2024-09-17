---
title: Overview
---

**LightAPI** is a **lightweight framework** designed for quickly building **API endpoints** using **Python**'s native libraries. 

It simplifies API development by providing a **minimal interface** while maintaining flexibility and performance through asynchronous programming.

## Key Features
- Async by Default: All endpoints are asynchronous by default, allowing for concurrent request handling.
- JWT Authentication by default: JWT authentication is built-in, providing secure access to API endpoints.
- Simplicity: Minimal code is required to define and register API endpoints.
- Flexibility: Easily define SQLAlchemy models and generate CRUD API endpoints for them.
- Performance: Powered by aiohttp to handle concurrent requests efficiently, ensuring high performance for asynchronous HTTP handling.
- Database Support: Supports multiple databases, including SQLite, PostgreSQL, MySQL, MariaDB, Oracle, and MS-SQL.
- Automatic Route Generation: RESTful endpoints are automatically created for each model, reducing the need for manual route definitions.

## How it Works
LightAPI integrates:
- SQLAlchemy for ORM and database interactions.
- aiohttp for managing async HTTP requests and routing.
By registering your SQLAlchemy models with LightAPI, it dynamically generates RESTful routes (POST, GET, PUT, PATCH, DELETE) for each model.

```python
from sqlalchemy import Column, String, Boolean
from lightapi import LightApi
from lightapi.database import Base

class Person(Base):
    name = Column(String)
    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)

if __name__ == '__main__':
    app = LightApi()
    app.register({'/person': Person})
    app.run()

```
This will create the following API endpoints for the Person model:

- POST /person/ - Create a new entry
- GET /person/ - Retrieve all entries
- GET /person/{id} - Retrieve an entry by ID
- PUT /person/{id} - Update an entry by ID
- PATCH /person/{id} - Partially update an entry by ID
- DELETE /person/{id} - Delete an entry by ID
- OPTIONS /person/ - Return allowed HTTP methods and headers
- HEAD /person/ - Return response headers only

## Using RestEndpoint for Custom Endpoints
LightAPI also allows you to create custom endpoints by subclassing the RestEndpoint class. This gives you more control over the routes and methods for each endpoint, while still automating common HTTP method handling.

Here’s an example of how to use the RestEndpoint class:
```python
from lightapi import LightApi
from lightapi.rest import RestEndpoint

class CustomEndpoint(RestEndpoint):
    tablename = 'users'
    http_method_names = ['GET', 'POST']  # Only allowing GET and POST requests
    # http_method_names = ['PUT', 'PATCH']  # or only allowing PUT and PATCH requests

    def get(self, request):
        return {'message': 'GET request to users'}

    def post(self, request):
        return {'message': 'POST request with data'}

if __name__ == '__main__':
    
    app = LightApi()
    app.register({
        '/custom': CustomEndpoint
    })
    app.run()

```
This example creates a UserEndpoint with two routes:

- GET /users/: Retrieves user information.
- POST /users/: Accepts JSON data and creates a new user.
You can define other methods (e.g., PUT, DELETE, etc.) or exclude them by customizing the http_method_names and http_exclude attributes.

