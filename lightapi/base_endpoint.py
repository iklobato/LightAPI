from http.server import BaseHTTPRequestHandler
from abc import ABC, abstractmethod


class MyBaseEndpoint(BaseHTTPRequestHandler, ABC):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

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


class Endpoint(MyBaseEndpoint, ABC):
    @abstractmethod
    def get(self, request):
        pass

    @abstractmethod
    def post(self, request):
        pass

    @abstractmethod
    def put(self, request):
        pass

    @abstractmethod
    def delete(self, request):
        pass
