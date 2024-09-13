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

## Example Usage:
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

## Testing Handlers
You can test the handlers directly without relying on a live server by using Python’s aiohttp client to simulate requests. Here is a sample script to test all endpoints:
```python
import aiohttp
import asyncio

BASE_URL = 'http://localhost:8080'

async def test_endpoints():
    async with aiohttp.ClientSession() as session:
        await session.post(f'{BASE_URL}/person/', json={ "name": "John Doe", "email": "john@example.com", "email_verified": True })
        await session.get(f'{BASE_URL}/person/')
        await session.get(f'{BASE_URL}/person/1')
        await session.put(f'{BASE_URL}/person/1', json={ "name": "Jane Doe", "email": "jane@example.com" })
        await session.patch(f'{BASE_URL}/person/1', json={ "email_verified": False })
        await session.delete(f'{BASE_URL}/person/1')
        await session.options(f'{BASE_URL}/person/')
        await session.head(f'{BASE_URL}/person/')

if __name__ == '__main__':
    asyncio.run(test_endpoints())
```

## Why LightAPI
LightAPI is designed to streamline API development by focusing on simplicity and speed. It’s ideal for prototyping, small projects, or situations where development speed is essential.

## Installation
### Install LightAPI via pip:
```bash
pip install LightApi
```

### Open Online
You can directly edit and test this project online using [Project IDX](https://idx.dev/). 

The repository includes pre-configured settings for the IDX environment (.idx folder). Simply click the link below to open the repository in Project IDX:

<a href="https://idx.google.com/import?url=https://github.com/iklobato/LightAPI.git">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://cdn.idx.dev/btn/open_dark_32.svg">
    <source
      media="(prefers-color-scheme: light)"
      srcset="https://cdn.idx.dev/btn/open_light_32.svg">
    <img
      height="32"
      alt="Open in IDX"
      src="https://cdn.idx.dev/btn/open_purple_32.svg">
  </picture>
</a>

### PyPI Page
LightApi on PyPI: https://pypi.org/project/LightApi/

## Contributing
Contributions are welcome! Fork the repository, submit a pull request, or open an issue for bugs or feature suggestions. The project’s philosophy emphasizes simplicity, so contributions should aim to enhance functionality while keeping the API minimal and intuitive.

## License
LightAPI is released under the MIT License. See the LICENSE file for details.

## Contact
For questions or feedback, reach out to Henrique Lobato at iklobato1@gmail.com

