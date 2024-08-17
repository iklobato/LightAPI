from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from database import Base, SessionLocal
from sqlalchemy.orm import Session
from aiohttp import web


def create_handler(model: Base):
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
class AbstractHandler(ABC):
    model: Base = field(default=None)

    @abstractmethod
    async def handle(self, db: Session, request: web.Request):
        raise NotImplementedError("Method not implemented")

    async def __call__(self, request: web.Request, *args, **kwargs):
        db: Session = SessionLocal()
        try:
            return await self.handle(db, request)
        finally:
            db.close()

    async def get_request_json(self, request: web.Request):
        return await request.json()

    def get_item_by_id(self, db: Session, item_id: int):
        return db.query(self.model).filter(self.model.pk == item_id).first()

    def add_and_commit_item(self, db: Session, item):
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def delete_and_commit_item(self, db: Session, item):
        db.delete(item)
        db.commit()

    def json_response(self, item, status=200):
        return web.json_response(item.serialize(), status=status)

    def json_error_response(self, error_message, status=404):
        return web.json_response({'error': error_message}, status=status)


class CreateHandler(AbstractHandler):
    async def handle(self, db, request):
        data = await self.get_request_json(request)
        item = self.model(**data)
        item = self.add_and_commit_item(db, item)
        return self.json_response(item, status=201)


class ReadHandler(AbstractHandler):
    async def handle(self, db, request):
        if 'id' not in request.match_info:
            items = db.query(self.model).all()
            response = [item.serialize() for item in items]
            return self.json_response(response, status=200)
        else:
            item_id = int(request.match_info['id'])
            item = self.get_item_by_id(db, item_id)
            if item:
                return self.json_response(item, status=200)
            else:
                return self.json_error_response('Item not found', status=404)


class UpdateHandler(AbstractHandler):
    async def handle(self, db, request):
        item_id = int(request.match_info['id'])
        item = self.get_item_by_id(db, item_id)
        if not item:
            return self.json_error_response('Item not found', status=404)

        data = await self.get_request_json(request)
        for key, value in data.items():
            setattr(item, key, value)

        item = self.add_and_commit_item(db, item)
        return self.json_response(item, status=200)


class PatchHandler(AbstractHandler):
    async def handle(self, db, request):
        item_id = int(request.match_info['id'])
        item = self.get_item_by_id(db, item_id)
        if not item:
            return self.json_error_response('Item not found', status=404)

        data = await self.get_request_json(request)
        for key, value in data.items():
            setattr(item, key, value)

        item = self.add_and_commit_item(db, item)
        return self.json_response(item, status=200)


class DeleteHandler(AbstractHandler):
    async def handle(self, db, request):
        item_id = int(request.match_info['id'])
        item = self.get_item_by_id(db, item_id)
        if not item:
            return self.json_error_response('Item not found', status=404)

        self.delete_and_commit_item(db, item)
        return web.Response(status=204)


class RetrieveAllHandler(AbstractHandler):
    async def handle(self, db, request):
        items = db.query(self.model).all()
        response = [item.serialize() for item in items]
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

