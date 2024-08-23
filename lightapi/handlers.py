import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from lightapi.database import Base, SessionLocal
from sqlalchemy.orm import Session
from aiohttp import web


def create_handler(model: Base):
    """
    Creates a list of route handlers for the given model.

    Args:
        model (Base): The SQLAlchemy model class for which to create handlers.

    Returns:
        list: A list of aiohttp web routes for the specified model.
    """
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
    """
    Abstract base class for handling HTTP requests related to a specific model.

    Attributes:
        model (Base): The SQLAlchemy model class to operate on.
    """

    model: Base = field(default=None)

    @abstractmethod
    async def handle(self, db: Session, request: web.Request):
        """
        Abstract method to handle the HTTP request.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Raises:
            NotImplementedError: If the method is not implemented by subclasses.
        """
        raise NotImplementedError("Method not implemented")

    async def __call__(self, request: web.Request, *args, **kwargs):
        """
        Calls the handler with the provided request.

        Args:
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The response returned by the handler.
        """
        db: Session = SessionLocal()
        try:
            return await self.handle(db, request)
        except Exception as e:
            logging.error(f"Error handling request: {e}")
            return web.json_response({'error': 'Internal server error!'}, status=500)
        finally:
            db.close()

    async def get_request_json(self, request: web.Request):
        """
        Extracts JSON data from the request body.

        Args:
            request (web.Request): The aiohttp web request object.

        Returns:
            dict: The JSON data from the request body.
        """
        try:
            return await request.json()
        except Exception as e:
            logging.error(f"Error parsing JSON from request: {e}")
            raise web.HTTPBadRequest(reason="Invalid JSON!")

    def get_item_by_id(self, db: Session, item_id: int):
        """
        Retrieves an item by its primary key.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            item_id (int): The primary key of the item to retrieve.

        Returns:
            Base: The item retrieved from the database, or None if not found.
        """
        try:
            return db.query(self.model).filter(self.model.pk == item_id).first()
        except Exception as e:
            logging.error(f"Error retrieving item by ID: {e}")
            raise web.HTTPBadRequest(reason="Error retrieving item by ID!")

    def add_and_commit_item(self, db: Session, item):
        """
        Adds and commits a new item to the database.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            item (Base): The item to add and commit.

        Returns:
            Base: The item after committing to the database.
        """
        try:
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        except Exception as e:
            logging.error(f"Error adding and commiting item: {e}")
            db.rollback()
            raise web.HTTPBadRequest(reason="Error saving item!")

    def delete_and_commit_item(self, db: Session, item):
        """
        Deletes and commits the removal of an item from the database.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            item (Base): The item to delete.
        """
        try:
            db.delete(item)
            db.commit()
        except Exception as e:
            logging.error(f"Error deleting and commiting item: {e}")
            db.rollback()
            raise web.HTTPBadRequest(reason="Error deleting and commiting item!")

    def json_response(self, item, status=200):
        """
        Creates a JSON response for the given item.

        Args:
            item (Base): The item to serialize and return.
            status (int, optional): The HTTP status code. Defaults to 200.

        Returns:
            web.Response: The JSON response containing the serialized item.
        """
        return web.json_response(item.serialize(), status=status)

    def json_error_response(self, error_message, status=404):
        """
        Creates a JSON response for an error message.

        Args:
            error_message (str): The error message to return.
            status (int, optional): The HTTP status code. Defaults to 404.

        Returns:
            web.Response: The JSON response containing the error message.
        """
        return web.json_response({'error': error_message}, status=status)


class CreateHandler(AbstractHandler):
    """
    Handles HTTP POST requests to create a new item.
    """

    async def handle(self, db, request):
        """
        Processes the POST request to create and save a new item.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The JSON response containing the created item.
        """
        try:
            data = await self.get_request_json(request)
            item = self.model(**data)
            item = self.add_and_commit_item(db, item)
            return self.json_response(item, status=201)
        except Exception as e:
            logging.error(f"Error creating item: {e}")
            return self.json_response("Error creating item!", status=400)


class ReadHandler(AbstractHandler):
    """
    Handles HTTP GET requests to retrieve one or all items.
    """

    async def handle(self, db, request):
        """
        Processes the GET request to retrieve an item by ID or all items.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The JSON response containing the item(s) or an error message.
        """
        if 'id' not in request.match_info:
            try:
                items = db.query(self.model).all()
                response = [item.serialize() for item in items]
                return self.json_response(response, status=200)
            except Exception as e:
                logging.error(f"Error retrieving an item by ID: {e}")
                return self.json_error_response("Error retrieving an item!", status=500)
        else:
            item_id = int(request.match_info['id'])
            item = self.get_item_by_id(db, item_id)
            if item:
                return self.json_response(item, status=200)
            else:
                return self.json_error_response('Item not found', status=404)


class UpdateHandler(AbstractHandler):
    """
    Handles HTTP PUT requests to update an existing item.
    """

    async def handle(self, db, request):
        """
        Processes the PUT request to update an existing item.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The JSON response containing the updated item or an error message.
        """
        item_id = int(request.match_info['id'])
        item = self.get_item_by_id(db, item_id)
        if not item:
            return self.json_error_response('Item not found', status=404)

        try:
            data = await self.get_request_json(request)
            for key, value in data.items():
                setattr(item, key, value)

            item = self.add_and_commit_item(db, item)
            return self.json_response(item, status=200)
        except Exception as e:
            logging.error(f"Error updating item: {e}")
            return self.json_response("Error updating item!", status=400)


class PatchHandler(AbstractHandler):
    """
    Handles HTTP PATCH requests to partially update an existing item.
    """

    async def handle(self, db, request):
        """
        Processes the PATCH request to partially update an existing item.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The JSON response containing the updated item or an error message.
        """
        item_id = int(request.match_info['id'])
        item = self.get_item_by_id(db, item_id)
        if not item:
            return self.json_error_response('Item not found', status=404)

        try:
            data = await self.get_request_json(request)
            for key, value in data.items():
                setattr(item, key, value)
            item = self.add_and_commit_item(db, item)
            return self.json_response(item, status=200)
        except Exception as e:
            logging.error(f"Error updating item: {e}")
            return self.json_response("Error patching item!", status=400)


class DeleteHandler(AbstractHandler):
    """
    Handles HTTP DELETE requests to delete an existing item.
    """

    async def handle(self, db, request):
        """
        Processes the DELETE request to remove an existing item.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: An empty response with status 204 if the item is deleted.
        """
        item_id = int(request.match_info['id'])
        item = self.get_item_by_id(db, item_id)
        if not item:
            return self.json_error_response('Item not found', status=404)

        try:
            self.delete_and_commit_item(db, item)
            return web.Response(status=204)
        except Exception as e:
            logging.error(f"Error deleting item: {e}")
            return self.json_response("Error deleting item!", status=400)


class RetrieveAllHandler(AbstractHandler):
    """
    Handles HTTP GET requests to retrieve all items.
    """

    async def handle(self, db, request):
        """
        Processes the GET request to retrieve all items.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The JSON response containing all items.
        """
        try:
            items = db.query(self.model).all()
            response = [item.serialize() for item in items]
            return web.json_response(response, status=200)
        except Exception as e:
            logging.error(f"Error retrieving all items: {e}")
            return self.json_response("Error retrieving all items!", status=500)


class OptionsHandler(AbstractHandler):
    """
    Handles HTTP OPTIONS requests to provide allowed methods and headers.
    """

    async def handle(self, db, request):
        """
        Processes the OPTIONS request to provide allowed methods and headers.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: The JSON response containing allowed methods and headers.
        """
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
    """
    Handles HTTP HEAD requests to check the resource existence.
    """

    async def handle(self, db, request):
        """
        Processes the HEAD request to check the resource existence.

        Args:
            db (Session): The SQLAlchemy session for database operations.
            request (web.Request): The aiohttp web request object.

        Returns:
            web.Response: An empty response with status 200.
        """
        return web.Response(status=200, headers={'Content-Type': 'application/json'})
