import unittest
from unittest.mock import MagicMock, patch
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from sqlalchemy.orm import Session
from handlers import CreateHandler, ReadHandler, UpdateHandler, DeleteHandler, PatchHandler, RetrieveAllHandler, OptionsHandler, HeadHandler
from models import Person


class TestHandlers(AioHTTPTestCase):

    async def get_application(self):
        app = web.Application()
        return app

    def setUp(self):
        super().setUp()
        self.db = MagicMock(spec=Session)
        self.request = MagicMock(spec=web.Request)
        self.person_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "email_verified": True
        }
        self.person = Person(**self.person_data)
        self.person.pk = 1

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_create_handler(self, mock_session):
        handler = CreateHandler(Person)
        self.request.json = MagicMock(return_value=self.person_data)

        response = await handler(self.request)
        response_json = await response.json()

        self.db.add.assert_called_once_with(self.person)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(self.person)

        self.assertEqual(response.status, 201)
        self.assertEqual(response_json, self.person.as_dict())

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_read_handler(self, mock_session):
        handler = ReadHandler(Person)
        self.db.query.return_value.filter.return_value.first.return_value = self.person
        self.request.match_info = {'id': '1'}

        response = await handler(self.request)
        response_json = await response.json()

        self.assertEqual(response.status, 200)
        self.assertEqual(response_json, self.person.as_dict())

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_update_handler(self, mock_session):
        handler = UpdateHandler(Person)
        updated_data = {"name": "Jane Doe"}
        self.request.match_info = {'id': '1'}
        self.request.json = MagicMock(return_value=updated_data)

        self.db.query.return_value.filter.return_value.first.return_value = self.person

        response = await handler(self.request)
        response_json = await response.json()

        self.assertEqual(response.status, 200)
        self.assertEqual(response_json['name'], "Jane Doe")

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_delete_handler(self, mock_session):
        handler = DeleteHandler(Person)
        self.request.match_info = {'id': '1'}
        self.db.query.return_value.filter.return_value.first.return_value = self.person

        response = await handler(self.request)

        self.db.delete.assert_called_once_with(self.person)
        self.db.commit.assert_called_once()

        self.assertEqual(response.status, 204)

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_patch_handler(self, mock_session):
        handler = PatchHandler(Person)
        patch_data = {"email_verified": False}
        self.request.match_info = {'id': '1'}
        self.request.json = MagicMock(return_value=patch_data)

        self.db.query.return_value.filter.return_value.first.return_value = self.person

        response = await handler(self.request)
        response_json = await response.json()

        self.assertEqual(response.status, 200)
        self.assertEqual(response_json['email_verified'], False)

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_retrieve_all_handler(self, mock_session):
        handler = RetrieveAllHandler(Person)
        self.db.query.return_value.all.return_value = [self.person]

        response = await handler(self.request)
        response_json = await response.json()

        self.assertEqual(response.status, 200)
        self.assertEqual(response_json, [self.person.as_dict()])

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_options_handler(self, mock_session):
        handler = OptionsHandler(Person)

        response = await handler(self.request)
        response_json = await response.json()

        self.assertEqual(response.status, 200)
        self.assertIn('allowed_methods', response_json)

    @unittest_run_loop
    @patch('handlers.SessionLocal', return_value=MagicMock(spec=Session))
    async def test_head_handler(self, mock_session):
        handler = HeadHandler(Person)

        response = await handler(self.request)

        self.assertEqual(response.status, 200)


if __name__ == '__main__':
    unittest.main()

