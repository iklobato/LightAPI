from abc import ABC
from typing import Type, Callable, List

from aiohttp import web
from sqlalchemy.orm import DeclarativeMeta

from lightapi.exceptions import MissingHandlerImplementationError
from lightapi.handlers import (
    CreateHandler,
    RetrieveAllHandler,
    ReadHandler,
    UpdateHandler,
    DeleteHandler,
    PatchHandler,
)


class RestEndpoint(ABC):
    """
    A generic REST API endpoint class that dynamically generates route handlers for common HTTP methods
    (POST, GET, PUT, DELETE, PATCH) based on the model provided, with optional JWT authentication.

    This class is designed to be subclassed for specific API endpoints. Subclasses must define a
    `tablename` to match the SQLAlchemy model and can override `http_verbs` and `http_exclude`
    to customize the supported HTTP methods.

    Attributes:
        model (Type[DeclarativeMeta]): The SQLAlchemy model associated with this endpoint.
        tablename (str): The name of the table or resource for this endpoint, used in route URLs.
        http_verbs (List[str]): A list of allowed HTTP methods for this endpoint. Defaults to all major verbs.
        http_exclude (List[str]): A list of HTTP methods to exclude from this endpoint's routes.
        authentication (bool): Specifies whether to require JWT authentication on all routes.

    Usage Example:
    --------------
    Define a custom endpoint by subclassing `RestEndpoint` and specifying the table and desired HTTP methods:

    ```python
    from yourproject.models import UserModel

    class UserEndpoint(RestEndpoint):
        tablename = 'users'
        http_verbs = ['get', 'post']  # Allow GET and POST methods only
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

    tablename: str
    http_verbs: List[str] = [
        'post', 'get', 'put', 'delete', 'patch', 'options', 'head'
    ]
    http_exclude: List[str] = []
    authentication_class: None

    def __init__(self, model: Type[DeclarativeMeta]) -> None:
        """
        Initializes the RestEndpoint with the provided SQLAlchemy model and sets up routes
        based on the allowed HTTP methods. If authentication is enabled, it uses the provided
        `DefaultJWT` instance to validate JWT tokens.

        Args:
            model (Type[DeclarativeMeta]): The SQLAlchemy model associated with this endpoint.
        """
        self.model = model
        self.routes: List[web.RouteDef] = self._create_routes()

    def _create_routes(self) -> List[web.RouteDef]:
        """
        Creates route definitions for the allowed HTTP methods, excluding any specified in `http_exclude`.

        The routes will map to common REST operations like Create (POST), Read (GET), Update (PUT/PATCH),
        and Delete (DELETE). If `authentication` is enabled, each request is authenticated via JWT.

        Raises:
            MissingHandlerImplementationError: If a required handler for a specific HTTP verb is not implemented.

        Returns:
            List[web.RouteDef]: A list of aiohttp route definitions.
        """
        available_verbs = set(self.http_verbs) - set(self.http_exclude)
        routes: List[web.RouteDef] = []

        for verb in available_verbs:
            if verb == 'post':
                routes.append(
                    web.post(
                        f'/{self.tablename}/',
                        self._auth_wrapper(self._create_handler('post', CreateHandler))
                    )
                )
            elif verb == 'get':
                routes.append(
                    web.get(
                        f'/{self.tablename}/',
                        self._auth_wrapper(self._create_handler('get', RetrieveAllHandler))
                    )
                )
                routes.append(
                    web.get(
                        f'/{self.tablename}/{{id}}',
                        self._auth_wrapper(self._create_handler('get', ReadHandler))
                    )
                )
            elif verb == 'put':
                routes.append(
                    web.put(
                        f'/{self.tablename}/{{id}}',
                        self._auth_wrapper(self._create_handler('put', UpdateHandler))
                    )
                )
            elif verb == 'delete':
                routes.append(
                    web.delete(
                        f'/{self.tablename}/{{id}}',
                        self._auth_wrapper(self._create_handler('delete', DeleteHandler))
                    )
                )
            elif verb == 'patch':
                routes.append(
                    web.patch(
                        f'/{self.tablename}/{{id}}',
                        self._auth_wrapper(self._create_handler('patch', PatchHandler))
                    )
                )

        return routes

    def _create_handler(self, verb: str, handler_class: Type[Callable]) -> Callable:
        """
        Instantiates the appropriate handler for a specific HTTP verb.

        Args:
            verb (str): The HTTP verb (e.g., 'get', 'post', etc.).
            handler_class (Type[Callable]): The class responsible for handling the request for the given HTTP verb.

        Raises:
            MissingHandlerImplementationError: If the handler for the given HTTP verb is not implemented.

        Returns:
            Callable: The handler for the specified HTTP verb.
        """
        if not hasattr(self, handler_class.__name__):
            raise MissingHandlerImplementationError(handler_class.__name__, verb)
        return handler_class(self.model)

    def _auth_wrapper(self, handler: Callable) -> Callable:
        """
        Wraps the request handler to enforce JWT authentication if enabled.

        Args:
            handler (Callable): The original handler for the route.

        Returns:
            Callable: The wrapped handler with optional authentication.
        """
        async def wrapped_handler(request: web.Request):
            if self.authentication_class:
                await self.authentication_class.authenticate_request(request)
            return await handler(request)

        return wrapped_handler

    def configure(self) -> None:
        """
        Abstract method for configuring any additional behaviors or settings for the endpoint.

        Subclasses should implement this method to add custom logic or configurations as necessary.
        """
        pass
