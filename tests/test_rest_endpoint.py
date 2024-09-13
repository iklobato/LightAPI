import unittest
from unittest.mock import MagicMock, patch
from aiohttp import web
from lightapi.exceptions import MissingHandlerImplementationError
from lightapi.rest import RestEndpoint


class TestRestEndpoint(unittest.TestCase):

    @patch('lightapi.rest.RestEndpoint._create_routes')
    def test_initialization(self, mock_create_routes):
        mock_create_routes.return_value = []
        endpoint = RestEndpoint()
        self.assertEqual(endpoint.routes, [])

    @patch('lightapi.rest.RestEndpoint._create_routes')
    def test_route_creation(self, mock_create_routes):
        mock_create_routes.return_value = [web.get('/test/', MagicMock())]
        endpoint = RestEndpoint()
        routes = endpoint._create_routes()
        self.assertTrue(any(route.method == 'GET' and route.path == '/test/' for route in routes))

    @patch('lightapi.rest.RestEndpoint._auth_wrapper')
    def test_handler_creation_with_auth(self, mock_auth_wrapper):
        mock_auth_wrapper.return_value = MagicMock()
        endpoint = RestEndpoint()
        endpoint.authentication_class = MagicMock()
        endpoint.authentication_class.authenticate_request = MagicMock()
        handler = endpoint._create_handler('get')
        self.assertTrue(handler)
        mock_auth_wrapper.assert_called()

    @patch('lightapi.rest.RestEndpoint._create_handler')
    def test_handler_execution(self, mock_create_handler):
        mock_create_handler.return_value = MagicMock()
        mock_create_handler.return_value = web.json_response({'key': 'value'})
        endpoint = RestEndpoint()
        request = MagicMock()
        request.method = 'GET'
        response = mock_create_handler('get')(request)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.json(), {'key': 'value'})

    @patch('lightapi.rest.RestEndpoint._auth_wrapper')
    def test_authentication(self, mock_auth_wrapper):
        mock_auth_wrapper.return_value = MagicMock()
        auth_class = MagicMock()
        auth_class.authenticate_request = MagicMock()
        endpoint = RestEndpoint()
        endpoint.authentication_class = auth_class
        handler = endpoint._create_handler('post')
        request = MagicMock()
        handler(request)
        auth_class.authenticate_request.assert_called_with(request)

    def test_missing_handler(self):
        class TestEndpoint(RestEndpoint):
            _tablename = 'test'

            def get(self, request):
                return {'message': 'success'}

        endpoint = TestEndpoint()
        with self.assertRaises(MissingHandlerImplementationError):
            endpoint._create_handler('delete')


if __name__ == '__main__':
    unittest.main()
