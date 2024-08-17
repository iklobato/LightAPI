import unittest
from unittest.mock import patch, MagicMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from sqlalchemy.orm import Session

from handlers import (
    CreateHandler, ReadHandler, UpdateHandler, DeleteHandler, RetrieveAllHandler,
    PatchHandler, OptionsHandler, HeadHandler, Base
)


class TestHandlers(AioHTTPTestCase):
    def setUp(self):
        super().setUp()
        self.model = MagicMock(spec=Base)
        self.model.__tablename__ = 'testmodel'

    async def test_create_handler(self):
        handler = CreateHandler(model=self.model)
        request = MagicMock()
        request.json = MagicMock(return_value={'field': 'value'})
        db_session = MagicMock(spec=Session)

        with patch('your_module.SessionLocal', return_value=db_session):
            response = await handler(request)

        self.assertEqual(response.status, 201)
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()

    async def test_read_handler(self):
        handler = ReadHandler(model=self.model)
        request = MagicMock()
        db_session = MagicMock(spec=Session)
        item = MagicMock()
        item.as_dict.return_value = {'id': 1, 'field': 'value'}

        db_session.query().filter().first.return_value = item
        request.match_info = {'id': '1'}

        with patch('your_module.SessionLocal', return_value=db_session):
            response = await handler(request)

        self.assertEqual(response.status, 200)
        self.assertEqual(await response.json(), {'id': 1, 'field': 'value'})

    async def test_update_handler(self):
        handler = UpdateHandler(model=self.model)
        request = MagicMock()
        request.json = MagicMock(return_value={'field': 'new_value'})
        db_session = MagicMock(spec=Session)
        item = MagicMock()
        item.as_dict.return_value = {'id': 1, 'field': 'new_value'}

        db_session.query().filter().first.return_value = item
        request.match_info = {'id': '1'}

        with patch('your_module.SessionLocal', return_value=db_session):
            response = await handler(request)

        self.assertEqual(response.status, 200)
        db_session.commit.assert_called_once()

    async def test_delete_handler(self):
        handler = DeleteHandler(model=self.model)
        request = MagicMock()
        db_session = MagicMock(spec=Session)
        item = MagicMock()

        db_session.query().filter().first.return_value = item
        request.match_info = {'id': '1'}

        with patch('your_module.SessionLocal', return_value=db_session):
            response = await handler(request)

        self.assertEqual(response.status, 204)
        db_session.commit.assert_called_once()

    async def test_retrieve_all_handler(self):
        handler = RetrieveAllHandler(model=self.model)
        request = MagicMock()
        db_session = MagicMock(spec=Session)
        item = MagicMock()
        item.as_dict.return_value = {'id': 1, 'field': 'value'}

        db_session.query().all.return_value = [item]

        with patch('your_module.SessionLocal', return_value=db_session):
            response = await handler(request)

        self.assertEqual(response.status, 200)
        self.assertEqual(await response.json(), [{'id': 1, 'field': 'value'}])

    async def test_options_handler(self):
        handler = OptionsHandler(model=self.model)
        request = MagicMock()

        response = await handler(request)

        self.assertEqual(response.status, 200)
        self.assertIn('allowed_methods', await response.json())

    async def test_head_handler(self):
        handler = HeadHandler(model=self.model)
        request = MagicMock()

        response = await handler(request)

        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')


if __name__ == '__main__':
    unittest.main()
