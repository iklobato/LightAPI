import logging

from aiohttp import web
from sqlalchemy.exc import SQLAlchemyError

from lightapi.database import Base, engine
from lightapi.handlers import create_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class CustomApplication(web.Application):
    """
    Custom web application class that extends aiohttp.web.Application.

    Methods:
        _handle: Handles incoming requests with additional logging.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initializes the CustomApplication instance.
        """

        super().__init__(*args, **kwargs)

    async def _handle(self, *args, **kwargs):
        """
        Handles incoming requests with logging.

        Returns:
            aiohttp.web.Response: The response from the handler.
        """

        logging.info(f"Handling request: {args}, {kwargs}")
        return super()._handle(*args, **kwargs)


class LightApi:
    """
    LightAPI framework class for managing routes and initializing the web application.

    This class is responsible for initializing the web application, registering
    models, and creating database tables using SQLAlchemy.

    Attributes:
        app (aiohttp.web.Application): The aiohttp application instance.
        routes (list): List of registered routes for the application.

    Methods:
        register: Registers API routes for SQLAlchemy models.
        run: Starts the web server and serves the application.

    Examples:
        ``` py
        api = LightApi()
        api.register({'/person': Person})
        api.run(host='0.0.0.0', port=8000)
        ```
    """
    
    def __init__(self):
        """
        Initializes the LightApi instance and creates database tables.

        Sets up the web application and attempts to create all database tables
        using SQLAlchemy. Logs any errors that occur during table creation.
        """
        self.app = web.Application()
        self.routes = []
        try:
            Base.metadata.create_all(bind=engine)
            logging.info(f"Tables successfully created and connected to {engine.url}")
        except SQLAlchemyError as e:
            logging.error(f"Error creating tables: {e}")

    def register(self, models: dict):
        """
        Registers API routes for the provided SQLAlchemy models.

        For each model provided, this method creates RESTful CRUD handlers
        and registers them as routes within the application.

        Args:
            models (dict): A dictionary where the keys are route paths (str)
            and the values are SQLAlchemy models.

        Examples:
            ``` py
            api = LightApi()
            api.register({'/person': Person})
            ```
        """
        for path, model in models.items():
            self.routes.extend(create_handler(model))

    def run(self, host='0.0.0.0', port=8000):
        """
        Starts the web server and serves the application.

        This method adds the registered routes to the application and runs the
        aiohttp web server on the specified host and port.

        Args:
            host (str, optional): The host IP to bind the server to. Defaults to '0.0.0.0'.
            port (int, optional): The port number to run the server on. Defaults to 8000.

        Examples:
            ``` py
            api = LightApi()
            api.run(host='127.0.0.1', port=8080)
            ```
        """
        self.app.add_routes(self.routes)
        web.run_app(self.app, host=host, port=port)
