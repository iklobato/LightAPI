import logging
from abc import abstractmethod
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from database import SessionLocal, CustomBase
from aiohttp import web


def create_handler(model: CustomBase):
    return [
        web.post(f'/{model.__tablename__}/', CreateHandler(model)),
        web.get(f'/{model.__tablename__}/', RetrieveAllHandler(model)),
        web.get(f'/{model.__tablename__}/{{id}}', ReadHandler(model)),
        web.put(f'/{model.__tablename__}/{{id}}', UpdateHandler(model)),
        web.delete(f'/{model.__tablename__}/{{id}}', DeleteHandler(model)),
        web.patch(f'/{model.__tablename__}/{{id}}', PatchHandler(model)),
        web.options(f'/{model.__tablename__}/', OptionsHandler(model)),
        web.head(f'/{model.__tablename__}/', HeadHandler(model)),
    ]


@dataclass
class AbstractHandler:
    model: CustomBase = field(default=None)

    @abstractmethod
    async def handle(self, db: Session, request: web.Request):
        raise NotImplementedError(f"Method not implemented")

    async def __call__(self, request: web.Request, *args, **kwargs):
        db: Session = SessionLocal()
        try:
            return await self.handle(db, request)
        finally:
            db.close()


class CreateHandler(AbstractHandler):
    async def handle(self, db, request):
        data = await request.json()
        item = self.model(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        logging.info(f"Created item: {item}")
        return web.json_response(item.as_dict(), status=201)


class ReadHandler(AbstractHandler):
    async def handle(self, db, request):
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


class UpdateHandler(AbstractHandler):
    async def handle(self, db, request):
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


class PatchHandler(AbstractHandler):
    async def handle(self, db, request):
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


class DeleteHandler(AbstractHandler):
    async def handle(self, db, request):
        item_id = int(request.match_info['id'])
        item = db.query(self.model).filter(self.model.pk == item_id).first()
        if not item:
            logging.info(f"Item with ID {item_id} not found")
            return web.json_response({'error': 'Item not found'}, status=404)

        db.delete(item)
        db.commit()
        logging.info(f"Deleted item with ID {item_id}")
        return web.Response(status=204)


class RetrieveAllHandler(AbstractHandler):
    async def handle(self, db, request):
        items = db.query(self.model).all()
        response = [item.as_dict() for item in items]
        logging.info(f"Retrieved all items: {response}")
        return web.json_response(response, status=200)


class OptionsHandler(AbstractHandler):
    async def handle(self, db, request):
        return web.json_response(
            {
                'allowed_methods': [
                    'GET',
                    'POST',
                    'PUT',
                    'DELETE',
                    'PATCH',
                    'OPTIONS',
                    'HEAD',
                ],
                'allowed_headers': ['Content-Type', 'Authorization'],
                'max_age': 3600,
            }
        )


class HeadHandler(AbstractHandler):
    async def handle(self, db, request):
        return web.Response(
            status=200, headers={'Content-Type': 'application/json'}
        )
