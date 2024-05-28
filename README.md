
[![Upload Python Package](https://github.com/henriqueblobato/LightAPI/actions/workflows/python-publish.yml/badge.svg)](https://github.com/henriqueblobato/LightAPI/actions/workflows/python-publish.yml)

# LightApi

## What is LightApi?

LightApi is a lightweight API framework designed for rapid development of RESTful APIs in Python. It provides a simple and intuitive interface for defining endpoints and handling HTTP requests without the need for complex configuration or dependencies.
This project dont use any external library to create the API, it uses the built-in `http.server` to create a minimalistic yet powerful API framework.

## How does it work?

LightApi leverages Python's built-in `http.server` module to create a minimalistic yet powerful API framework. It allows you to define endpoints using familiar Python classes and methods, making it easy to map HTTP requests to Python code.

## Key Features:

- Lightweight and easy to use.
- Minimal dependencies.
- Automatic generation of CRUD endpoints for data models.
- Designed for rapid development and prototyping.

## Why use LightApi?

### Simplicity:

LightApi provides a simple and straightforward API for defining endpoints and handling HTTP requests. You can get started with just a few lines of code, without the need for complex configuration or setup.

### Flexibility:

With LightApi, you have full control over how your API endpoints are defined and how requests are processed. You can easily customize middleware, error handling, and request/response processing to suit your specific requirements.

### Performance:

LightApi is designed to be lightweight and efficient, with minimal overhead. It leverages Python's built-in `http.server` module for request handling, ensuring optimal performance and scalability.

### Rapid Development:

LightApi is perfect for rapid development and prototyping of RESTful APIs. It allows you to quickly define endpoints, test them locally, and iterate on your API design without getting bogged down in unnecessary complexity.

## Caveats:

- LightApi is intended for use in development and prototyping environments only. The built-in `http.server` module used by LightApi is not suitable for production use, as it lacks features such as concurrency, scalability, and security.

## Getting Started:

To get started with LightApi, simply install the package using pip:

```
pip install lightapi
```

Then, define your API endpoints using Python classes and methods, and run your API using the `LightApi` class:

```python
from lightapi import LightApi

# Define your API endpoints here...

app = LightApi()
# Register your endpoints with the app...
app.run()
```

## Example:
Registering a person endpoint:

```python
from dataclasses import dataclass
from typing import Optional
from lightapi import LightApi
from lightapi.handlers import BaseModel

@dataclass
class Person(BaseModel):
    name: str
    age: int
    email: Optional[str] = None
    
app = LightApi()
app.endpoint(Person)
app.run()

```

This will create all REST endpoints:
```http request
GET /person
GET /person/{id}
POST /person
DELETE /person/{id}
PUT /person/{id}
```
with all CRUD operations.

## Contributing:

This project is currently in the early stages of development, and contributions are welcome!
If you find any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request on GitHub. Your contributions are greatly appreciated!

## GOAL
The goal of the project is to develop a python minimal api interface that can be used to create RESTful APIs with minimal effort and dependencies.
This library will install as minimum third party libraries as possible in order to keep it lightweight and easy to use.

## License:

LightApi is licensed under the MIT License. See the [LICENSE](https://github.com/example/lightapi/blob/main/LICENSE) file for details.
