import logging
from dataclasses import dataclass, fields, field
from abc import ABC
from typing import Type, TypeVar, get_type_hints
import json

T = TypeVar('T')


class MultiEndpointHandlerSingleton(type):
    """
    Ensures all endpoints uses the same instance of MultiEndpointHandler .
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            logging.debug(f"Creating new instance of {cls}")
            cls._instances[cls] = super(MultiEndpointHandlerSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MultiEndpointHandler(metaclass=MultiEndpointHandlerSingleton):
    def __init__(self, *endpoints):
        self.endpoints = endpoints

    def handle_request(self, handler):
        for endpoint in self.endpoints:
            if handler.path.startswith(endpoint.path_prefix):
                logging.debug(f"Handling request for {endpoint.__name__}")
                return endpoint(handler)
        handler.send_error(404, 'Not Found')

    def __call__(self, *args, **kwargs):
        return self.handle_request(*args, **kwargs)


@dataclass
class BaseModel(ABC):
    """
    Base model is responsible to map all classes parameters into a valid
    api endpoint. Need to use dataclass syntax to define the class as an endpoint.
    This class maps for example:

        @dataclass
        class Person(BaseModel):
            name: str
            age: int
            email: Optional[str] = None

    into:
        HTTP POST /person
            {
            "name": "John Doe",
            "age": 30,
            "email": ""
            }
        HTTP GET /person
            {
            "name": "John Doe",
            "age": 30,
            "email": ""
            }
        HTTP GET /person/1
            {
            "name": "John Doe",
            "age": 30,
            "email": ""
            }
        HTTP PUT /person
            {
            "name": "John Doe",
            "age": 30,
            "email": ""
            }
        HTTP DELETE /person
            {
            "name": "John Doe",
            "age": 30,
            "email": ""
            }

    """

    @property
    def url(self):
        return f'/{self.__class__.__name__.lower()}'

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        return cls.from_dict(json.loads(json_data))
