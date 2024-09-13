import logging
from abc import ABC
from enum import Enum
from typing import Type, Callable, List, Set

from aiohttp import web

from lightapi.exceptions import MissingHandlerImplementationError


class HttpEnum(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RestEndpoint(ABC):
    """
    A generic REST API endpoint class that dynamically generates route handlers for common HTTP methods
    (POST, GET, PUT, DELETE, PATCH) based on the model provided, with optional JWT authentication.

    This class is designed to be subclassed for specific API endpoints. Subclasses must define a
    `tablename` to match the SQLAlchemy model and can override `http_verbs` and `http_exclude`
    to customize the supported HTTP methods.

    Attributes:
        http_method_names (List[str]): A list of allowed HTTP methods for this endpoint. Defaults to all major verbs.
        http_exclude (List[str]): A list of HTTP methods to exclude from this endpoint's routes.
        authentication_class (Type[AbstractAuthentication]): The class responsible for authenticating requests.

    Usage Example:
    --------------
    Define a custom endpoint by subclassing `RestEndpoint` and specifying the table and desired HTTP methods:

    ```python
    from yourproject.models import UserModel

    class UserEndpoint(RestEndpoint):
        tablename = 'users'
        http_method_names = ['get', 'post']  # Allow GET and POST methods only
        authentication = True  # Enable JWT authentication

        def configure(self):
            # Optional configuration logic
            pass
    ```

    In your web server initialization, register the endpoint:

    ```python
    app = web.Application()
    user_endpoint = UserEndpoint(UserModel)
    app.add_routes(user_endpoint.routes)
    web.run_app(app, host='0.0.0.0', port=8000)
    ```

    This will automatically create the following routes:
    - `POST /users/` for creating a new user.
    - `GET /users/` for retrieving all users.
    - `GET /users/{id}` for retrieving a user by ID.

    If `authentication` is enabled, JWT validation will occur before handling each request.
    """

    _tablename: str
    http_method_names: Set[str] = [method.value for method in HttpEnum]
    http_exclude: List[str] = list()
    authentication_class: None

    def __init__(self) -> None:
        """
        Initializes the RestEndpoint with the provided SQLAlchemy model and sets up routes
        based on the allowed HTTP methods. If authentication is enabled, it uses the provided
        `DefaultJWT` instance to validate JWT tokens.
        """
        self.routes: List[web.RouteDef] = self._create_routes()

    @property
    def tablename(self) -> str:
        """
        Getter for the tablename attribute.

        Returns:
            str: The name of the table or resource for this endpoint.
        """
        return self._tablename

    def _create_routes(self) -> List[web.RouteDef]:
        available_verbs = set(self.http_method_names) - set(self.http_exclude)
        routes: List[web.RouteDef] = []

        if 'POST' in available_verbs:
            routes.append(web.post(f'/{self.tablename}/', self._create_handler('post')))
        if 'GET' in available_verbs:
            routes.append(web.get(f'/{self.tablename}/', self._create_handler('get')))
            # routes.append(web.get(f'/{self.tablename}/{{id}}', self._create_handler('get')))
        if 'PUT' in available_verbs:
            routes.append(
                web.put(f'/{self.tablename}/{{id}}', self._create_handler('put'))
            )
        if 'DELETE' in available_verbs:
            routes.append(
                web.delete(f'/{self.tablename}/{{id}}', self._create_handler('delete'))
            )
        if 'PATCH' in available_verbs:
            routes.append(
                web.patch(f'/{self.tablename}/{{id}}', self._create_handler('patch'))
            )
        if 'OPTIONS' in available_verbs:
            routes.append(
                web.options(f'/{self.tablename}/', self._create_handler('options'))
            )
        if 'HEAD' in available_verbs:
            routes.append(web.head(f'/{self.tablename}/', self._create_handler('head')))

        logging.debug(f"Available endpoints for {self.tablename}: {available_verbs}")
        return routes

    def _create_handler(self, method_name: str) -> Callable:
        async def handler(request: web.Request):
            method = getattr(self, method_name, None)
            if not method:
                raise MissingHandlerImplementationError(
                    f"Handler for {method_name} not implemented.", method_name
                )
            response = method(request)
            if isinstance(response, dict):
                return web.json_response(response)
            return response

        return handler

    # def _auth_wrapper(self, handler: Callable) -> Callable:
    #     """
    #     Wraps the request handler to enforce JWT authentication if enabled.
    #
    #     Args:
    #         handler (Callable): The original handler for the route.
    #
    #     Returns:
    #         Callable: The wrapped handler with optional authentication.
    #     """
    #     async def wrapped_handler(request: web.Request):
    #         if self.authentication_class:
    #             await self.authentication_class.authenticate_request(request)
    #         return await handler(request)
    #
    #     return wrapped_handler

    def configure(self) -> None:
        """
        Abstract method for configuring any additional behaviors or settings for the endpoint.

        Subclasses should implement this method to add custom logic or configurations as necessary.
        """
        pass
