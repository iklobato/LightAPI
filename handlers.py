import logging
from http.server import HTTPServer

from base_endpoint import Handler


# T = TypeVar('T')


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


class HTTPServerSingleton(type):
    """
    Ensures all endpoints uses the same instance of HTTPServer.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            logging.debug(f"Creating new instance of {cls}")
            cls._instances[cls] = super(HTTPServerSingleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class CustomHTTPServer(HTTPServer):
    _endpoints = {}

    def __init__(self, *args, **kwargs):
        # self.endpoints = kwargs.pop('endpoints', {})
        super().__init__(*args, **kwargs)

    def get_request(self):
        return super().get_request()

    @property
    def endpoints(self):
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value):
        self._endpoints = value


class LightApiServer(metaclass=HTTPServerSingleton):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.endpoints = []

    # def endpoint(self, path_prefix: str, endpoint_class: TypeVar):
    #     self.endpoints.append((path_prefix, endpoint_class))

    def run(self, host='0.0.0.0', port=8000):
        if not self.endpoints:
            raise RuntimeError("No endpoints registered.")

        server_address = (host, port)
        httpd = CustomHTTPServer(server_address, Handler)
        httpd.endpoints = self.endpoints
        logging.info(f'Starting httpd server on {host} port {port}...')

        httpd.serve_forever()
        # for endpoint in self.endpoints:
        #     logging.info(f"Endpoint {endpoint.__name__} URL: {endpoint().url}")
