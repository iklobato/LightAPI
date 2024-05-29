from database import engine, CustomBase

import logging
from aiohttp import web

from handlers import create_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


class CustomApplication(web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _handle(self, *args, **kwargs):
        logging.info(f"Handling request: {args}, {kwargs}")
        return super()._handle(*args, **kwargs)


class LightApi:
    def __init__(self):
        self.app = web.Application()
        self.routes = []

    def register(self, models: dict):
        for path, model in models.items():
            self.routes.extend(create_handler(model))
        CustomBase.metadata.create_all(bind=engine)

    def run(self, host='0.0.0.0', port=8000):
        self.app.add_routes(self.routes)
        web.run_app(self.app, host=host, port=port)
