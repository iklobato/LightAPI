# LightAPI

## Overview
LightAPI is a lightweight framework designed for quickly building API endpoints using Python's native libraries. It simplifies API development by providing a minimal interface while maintaining flexibility and performance through asynchronous programming.

## Features
- Simplicity: Define API endpoints with minimal boilerplate code.
- Flexibility: Define models using SQLAlchemy's ORM and create API endpoints for CRUD operations easily.
- Performance: Utilizes aiohttp for handling concurrent requests efficiently.

## How it Works
LightAPI leverages:
- SQLAlchemy for defining database models and interacting with databases.
- aiohttp for handling async HTTP requests and routing.

## Using LightAPI
Import the LightApi class, define your models using SQLAlchemy, and create an instance of LightApi to register your models. The framework automatically creates RESTful endpoints for each model.

## Example Usage: Model
```python
from sqlalchemy import Column, Integer, String, Boolean
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

## Example Usage: Custom Endpoints
Custom Endpoints with RestEndpoint
LightAPI is not limited to auto-generated CRUD endpoints. You can also create custom endpoints by subclassing RestEndpoint for complete control.

Example: Custom User Endpoint
```python
from lightapi import LightApi
from lightapi.rest import RestEndpoint

class CustomEndpoint(RestEndpoint):
    http_method_names = ['GET', 'POST']  # Only allow GET and POST requests

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

## API Endpoints
LightAPI automatically generates the following endpoints for each model:

| HTTP Method | Endpoint Example          | Handler Class          | Description                                              |
|-------------|---------------------------|------------------------|----------------------------------------------------------|
| POST        | /person/                  | CreateHandler          | Creates a new item in the `person` model                 |
| GET         | /person/                  | RetrieveAllHandler     | Retrieves all items from the `person` model              |
| GET         | /person/{id}              | ReadHandler            | Retrieves a specific item by ID from the `person` model  |
| PUT         | /person/{id}              | UpdateHandler          | Updates an existing item by ID in the `person` model     |
| PATCH       | /person/{id}              | PatchHandler           | Partially updates an existing item by ID in the `person` model |
| DELETE      | /person/{id}              | DeleteHandler          | Deletes an existing item by ID in the `person` model     |
| OPTIONS     | /person/                  | OptionsHandler         | Returns allowed HTTP methods and headers for the `person` model |
| HEAD        | /person/                  | HeadHandler            | Returns response headers only for the `person` model     |


## Databases Compatibility
LightAPI supports the following databases:
- SQLite
- PostgreSQL
- MySQL
- MariaDB
- Oracle
- MS-SQL

## Connecting to a Database
Set the DATABASE_URL environment variable to connect to your database:
```python
import os
os.environ['DATABASE_URL'] = "postgresql://user:password@postgresserver/db"
```
if no DATABASE_URL is provided, LightAPI defaults to using an in-memory SQLite database.

## Why LightAPI
LightAPI is designed to streamline API development by focusing on simplicity and speed. It’s ideal for prototyping, small projects, or situations where development speed is essential.

## Installation
### Install LightAPI via pip:
```bash
pip install LightApi
```

### PyPI Page
LightApi on PyPI: https://pypi.org/project/LightApi/

## Contributing
Contributions are welcome! Fork the repository, submit a pull request, or open an issue for bugs or feature suggestions. The project’s philosophy emphasizes simplicity, so contributions should aim to enhance functionality while keeping the API minimal and intuitive.

## License
LightAPI is released under the MIT License. See the LICENSE file for details.

## Contact
For questions or feedback, reach out to Henrique Lobato at iklobato1@gmail.com

