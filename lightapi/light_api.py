import json
import logging
from dataclasses import field, dataclass
from http.server import HTTPServer
from lightapi.base_endpoint import Endpoint
from lightapi.handlers import BaseModel
from typing import Type, Any, Union


@dataclass
class LightApi:
    endpoints: list = field(default_factory=list)

    def endpoint(self, endpoint_class: Union[Type[Endpoint], Type[BaseModel]]):
        if issubclass(endpoint_class, Endpoint):
            logging.debug(f"Endpoint type {endpoint_class} is a subclass of Endpoint")
            self.endpoints.append(endpoint_class)
        elif issubclass(endpoint_class, BaseModel):
            logging.debug(f"Endpoint type {endpoint_class} is a subclass of BaseModel")
            self.endpoints.append(self.create_endpoint_from_model(endpoint_class))
        else:
            raise ValueError("Provided class must be a subclass of Endpoint or BaseModel")

    def create_endpoint_from_model(self, model_class: Type[BaseModel]) -> Type[Endpoint]:
        class AutoEndpoint(Endpoint):
            def get(self, request: model_class):
                response = {"message": f"Received GET request with {request}"}
                self.respond(body=json.dumps(response))

            def post(self, request: model_class):
                response = {"message": f"Received POST request with {request}"}
                self.respond(body=json.dumps(response))

            def put(self, request: model_class):
                response = {"message": f"Received PUT request with {request}"}
                self.respond(body=json.dumps(response))

            def delete(self, request: model_class):
                response = {"message": f"Received DELETE request with {request}"}
                self.respond(body=json.dumps(response))

        return AutoEndpoint

    def run(self, host='0.0.0.0', port=8000):
        if not self.endpoints:
            raise RuntimeError("No endpoints registered.")

        handler = MultiEndpointHandler(*self.endpoints)
        server_address = (host, port)
        httpd = HTTPServer(server_address, handler)
        logging.info(f'Starting httpd server on {host} port {port}...')

        for endpoint in self.endpoints:
            logging.info(f"Endpoint {endpoint.__name__} URL: {endpoint().url}")

        httpd.serve_forever()

        logging.info(f'Ready to serve on {host}:{port}...')

