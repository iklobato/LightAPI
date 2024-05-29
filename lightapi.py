import logging
from aiohttp import web
from sqlalchemy.orm import Session
from database import SessionLocal, engine, CustomBase
from typing import Type


class LightApiHandler:
    def __init__(self, model):
        self.model = model

    async def handle_create(self, request):
        data = await request.json()
        db: Session = SessionLocal()
        try:
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

    async def handle_read(self, request):
        db: Session = SessionLocal()
        try:
            if hasattr(request.match_info, 'id') is False:
                items = db.query(self.model).all()
                response = [item.as_dict() for item in items]
            else:
                item_id = int(request.match_info['id'])
                item = db.query(self.model).filter(self.model.pk == item_id).first()
                if item:
                    response = item.as_dict()
                else:
                    logging.info(f"Item with ID {item_id} not found")
                    return web.json_response({'error': 'Item not found'}, status=404)

            logging.info(f"Retrieved item(s): {response}")
            return web.json_response(response, status=200)
        except Exception as e:
            logging.error(f"Error reading item(s): {e}")
            raise
        finally:
            db.close()

    async def handle_update(self, request):
        data = await request.json()
        db: Session = SessionLocal()
        try:
            item_id = int(request.match_info['id'])
            item = db.query(self.model).filter(self.model.pk == item_id).first()
            if not item:
                logging.info(f"Item with ID {item_id} not found")
                return web.json_response({'error': 'Item not found'}, status=404)

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

    async def handle_delete(self, request):
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


def create_handler(model: Type[CustomBase]):
    handler = LightApiHandler(model)
    return [
        web.post(f'/{model.__tablename__}/', handler.handle_create),
        web.get(f'/{model.__tablename__}/', handler.handle_read),
        web.get(f'/{model.__tablename__}/{{id}}', handler.handle_read),
        web.put(f'/{model.__tablename__}/{{id}}', handler.handle_update),
        web.delete(f'/{model.__tablename__}/{{id}}', handler.handle_delete),
    ]


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
