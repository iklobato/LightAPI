from unittest import TestCase
from unittest.mock import MagicMock, patch
from aiohttp import web
from lightapi.rest import RestEndpoint


class TestRestEndpointAuthentication(TestCase):

    def setUp(self):
        class MockEndpoint(RestEndpoint):
            tablename = 'mock_table'
            authentication_class = MagicMock()  # Mock authentication class

            def get(self, request):
                return web.json_response({"message": "Success", "user": request['user']})

        self.mock_endpoint = MockEndpoint()
        self.mock_request = MagicMock()

    @patch('lightapi.auth.DefaultJWTAuthentication')
    def test_authentication_success(self, MockJWTAuth):
        mock_auth = MockJWTAuth.return_value
        mock_auth.authenticate = MagicMock(return_value={'user_id': 1, 'username': 'test_user'})

        self.mock_request.headers = {'Authorization': 'Bearer valid.jwt.token'}

        handler = self.mock_endpoint._create_handler('get')
        response = handler(self.mock_request)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.json(), {"message": "Success", "user": {'user_id': 1, 'username': 'test_user'}})

    @patch('lightapi.auth.DefaultJWTAuthentication')
    def test_authentication_failure(self, MockJWTAuth):
        mock_auth = MockJWTAuth.return_value
        mock_auth.authenticate = MagicMock(side_effect=web.HTTPUnauthorized)

        self.mock_request.headers = {'Authorization': 'Bearer invalid.jwt.token'}

        handler = self.mock_endpoint._create_handler('get')
        with self.assertRaises(web.HTTPUnauthorized):
            handler(self.mock_request)
