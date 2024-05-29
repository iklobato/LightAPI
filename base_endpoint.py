import json
import logging
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler


class Endpoint:

    def as_dict(self):
        return asdict(self)


class MultiEndpointHandlerSingleton(type):
    """
    Ensures all endpoints uses the same instance of MultiEndpointHandler .
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            logging.debug(f"Creating new instance of {cls}")
            cls._instances[cls] = super(MultiEndpointHandlerSingleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class Handler(BaseHTTPRequestHandler, metaclass=MultiEndpointHandlerSingleton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def map_endpoints(self, url):
        obj = self.server.endpoints.get(url)
        if not obj:
            return None
        return obj

    def do_GET(self):
        obj = self.map_endpoints(self.path)
        if hasattr(obj, 'get'):
            response = obj.get()
            obj_json = json.dumps(response)
            self.respond(body=obj_json)
        else:
            return asdict(obj)

    def do_POST(self):
        # self.handle_request()
        obj = self.map_endpoints(self.path)
        if hasattr(obj, 'post'):
            response = obj.post()
            # TODO save on sqlite
            obj_json = json.dumps(response)
            self.respond(body=obj_json)
        else:
            response = obj.as_dict()
            return self.respond(body=json.dumps(response))

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        method = self.command
        if hasattr(self, method.lower()):
            handler = getattr(self, method.lower())
            handler(self)
        else:
            self.send_error(405, 'Method Not Allowed')

    def respond(self, status_code=200, content_type='application/json', body=None):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        if body:
            self.wfile.write(body.encode('utf-8'))
