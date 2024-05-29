from database import engine, CustomBase
from typing import Type

import logging
from aiohttp import web
from sqlalchemy.orm import Session
from database import SessionLocal


class CreateHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        db: Session = SessionLocal()
        try:
            data = await request.json()
            item = self.model(**data)
            db.add(item)
            db.commit()
            db.refresh(item)
            logging.info(f"Created item: {item}")
            return web.json_response(item.as_dict(), status=201)
        except Exception as e:
            logging.error(f"Error creating item: {e}")
            raise
        finally:
            db.close()


class ReadHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        db: Session = SessionLocal()
        try:
            if 'id' not in request.match_info:
                items = db.query(self.model).all()
                response = [item.as_dict() for item in items]
                logging.info(f"Retrieved item(s): {response}")
                return web.json_response(response, status=200)
            else:
                item_id = int(request.match_info['id'])
                item = db.query(self.model).filter(self.model.pk == item_id).first()
                if item:
                    logging.info(f"Retrieved item: {item.as_dict()}")
                    return web.json_response(item.as_dict(), status=200)
                else:
                    logging.info(f"Item with ID {item_id} not found")
                    return web.json_response({'error': 'Item not found'}, status=404)
        except Exception as e:
            logging.error(f"Error reading item(s): {e}")
            raise
        finally:
            db.close()


class UpdateHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        db: Session = SessionLocal()
        try:
            item_id = int(request.match_info['id'])
            item = db.query(self.model).filter(self.model.pk == item_id).first()
            if not item:
                logging.info(f"Item with ID {item_id} not found")
                return web.json_response({'error': 'Item not found'}, status=404)

            data = await request.json()
            for key, value in data.items():
                setattr(item, key, value)

            db.commit()
            db.refresh(item)
            logging.info(f"Updated item: {item}")
            return web.json_response(item.as_dict(), status=200)
        except Exception as e:
            logging.error(f"Error updating item: {e}")
            raise
        finally:
            db.close()


class PatchHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        db: Session = SessionLocal()
        try:
            item_id = int(request.match_info['id'])
            item = db.query(self.model).filter(self.model.pk == item_id).first()

            if not item:
                return web.json_response({'error': 'Item not found'}, status=404)

            data = await request.json()
            for key, value in data.items():
                setattr(item, key, value)

            db.commit()
            db.refresh(item)

            logging.info(f"Updated item: {item}")
            return web.json_response(item.as_dict(), status=200)
        except Exception as e:
            logging.error(f"Error updating item: {e}")
            raise
        finally:
            db.close()


class DeleteHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        db: Session = SessionLocal()
        try:
            item_id = int(request.match_info['id'])
            item = db.query(self.model).filter(self.model.pk == item_id).first()
            if not item:
                logging.info(f"Item with ID {item_id} not found")
                return web.json_response({'error': 'Item not found'}, status=404)

            db.delete(item)
            db.commit()
            logging.info(f"Deleted item with ID {item_id}")
            return web.Response(status=204)
        except Exception as e:
            logging.error(f"Error deleting item: {e}")
            raise
        finally:
            db.close()


class RetrieveAllHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        db: Session = SessionLocal()
        try:
            items = db.query(self.model).all()
            response = [item.as_dict() for item in items]
            logging.info(f"Retrieved all items: {response}")
            return web.json_response(response, status=200)
        except Exception as e:
            logging.error(f"Error retrieving all items: {e}")
            raise
        finally:
            db.close()


class OptionsHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        try:
            return web.json_response({
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'],
                'allowed_headers': ['Content-Type', 'Authorization'],
                'max_age': 3600
            })
        except Exception as e:
            logging.error(f"Error retrieving options: {e}")
            raise


class HeadHandler:
    def __init__(self, model):
        self.model = model

    async def handle(self, request):
        try:
            return web.Response(status=200, headers={'Content-Type': 'application/json'})
        except Exception as e:
            logging.error(f"Error retrieving headers: {e}")
            raise


def create_handler(model: Type[CustomBase]):
    handler = CreateHandler(model)
    read_all_handler = RetrieveAllHandler(model)
    read_one_handler = ReadHandler(model)
    update_handler = UpdateHandler(model)
    delete_handler = DeleteHandler(model)
    patch_handler = PatchHandler(model)
    options_handler = OptionsHandler(model)
    head_handler = HeadHandler(model)

    return [
        web.post(f'/{model.__tablename__}/', handler.handle),
        web.get(f'/{model.__tablename__}/', read_all_handler.handle),
        web.get(f'/{model.__tablename__}/{{id}}', read_one_handler.handle),
        web.put(f'/{model.__tablename__}/{{id}}', update_handler.handle),
        web.delete(f'/{model.__tablename__}/{{id}}', delete_handler.handle),
        web.patch(f'/{model.__tablename__}/{{id}}', patch_handler.handle),
        web.options(f'/{model.__tablename__}/', options_handler.handle),
        web.head(f'/{model.__tablename__}/', head_handler.handle)
    ]


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
