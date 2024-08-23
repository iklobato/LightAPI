from sqlalchemy.exc import SQLAlchemyError

from lightapi.database import engine, Base
from lightapi.handlers import create_handler

import logging
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class CustomApplication(web.Application):
    """
        Add request logging to the custom application class.

        Inherits from aiohttp.web.Application
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _handle(self, *args, **kwargs):
        """
        Override the request handling method to add logging.

        """
        logging.info(f"Handling request: {args}, {kwargs}")
        return super()._handle(*args, **kwargs)


class LightApi:
    """
        Main application class for LightAPI.

        Initializer the application, registering routes, and run the server.
    """


def __init__(self):
    self.app = web.Application()
    self.routes = []
    try:
        Base.metadata.create_all(bind=engine)
        logging.info(f"Tables successfully created and connected to {engine.url}")
    except SQLAlchemyError as e:
        logging.error(f"Error creating tables: {e}")


def register(self, models: dict):
    """
    Register a model and the routers with the application.

    """
    for path, model in models.items():
        self.routes.extend(create_handler(model))


def run(self, host='0.0.0.0', port=8000):
    """
    Start the web server.

    """
    self.app.add_routes(self.routes)
    try:
        web.run_app(self.app, host=host, port=port)
    except Exception as e:
        logging.error(f"Error running app: {e}")
