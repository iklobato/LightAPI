import unittest
from unittest.mock import patch, MagicMock
from aiohttp import web
import jwt
from lightapi.auth import DefaultJWTAuthentication


class TestTokenEncodingDecoding(unittest.TestCase):
    """
    Test case for methods related to encoding and decoding JWT tokens in DefaultJWTAuthentication.

    Methods tested:
    - encode_token: Verifies the JWT encoding with a valid secret key.
    - decode_token: Ensures that decoding works correctly for valid tokens, and handles
      invalid and expired tokens appropriately.
    """

    def setUp(self):
        """Set up an instance of DefaultJWTAuthentication and mock data for testing."""
        self.auth = DefaultJWTAuthentication()
        self.user_info = {'user_id': '123'}
        self.secret_key = 'testsecret'
        self.token = jwt.encode(self.user_info, self.secret_key, algorithm=self.auth.ALGORITHM)

    def test_encode_token(self):
        """
        Test the encode_token method.

        Verifies that the token is correctly generated with the provided user info and secret key.
        """
        token = self.auth.encode_token(self.user_info.get('user_id'))

        decoded_payload = self.auth.decode_token(token)
        self.assertEqual(decoded_payload['user_id'], self.user_info['user_id'])
        self.assertIn('exp', decoded_payload)

    def test_decode_token_invalid_signature(self):
        """
        Test the decode_token method with an invalid signature.

        Ensures that an HTTPUnauthorized error is raised when the token signature is invalid.
        """
        with self.assertRaises(web.HTTPUnauthorized):
            self.auth.decode_token(self.token)

    # @patch('lightapi.auth.DefaultJWTAuthentication.encode_token', return_value='invalid_secret')
    # def test_expired_token(self, mock_encode_token):
    #     """
    #     Test the decode_token method with an expired token.
    #
    #     Ensures that an HTTPUnauthorized error is raised for expired tokens.
    #     """
    #     payload = {
    #         'user_id': '1',
    #         'exp': datetime.utcnow().timestamp()
    #     }
    #     token = jwt.encode(payload, self.secret_key, algorithm=self.auth.ALGORITHM)
    #     with patch('lightapi.auth.DefaultJWTAuthentication.secret_key', return_value=self.secret_key):
    #         with self.assertRaises(web.HTTPUnauthorized):
    #             self.auth.decode_token(token)


class TestModelCreation(unittest.TestCase):
    """
    Test case for the model creation logic in DefaultJWTAuthentication.

    This class ensures that the necessary database tables are created for the user and token models
    if they don't already exist.
    """

    def setUp(self):
        """Set up an instance of DefaultJWTAuthentication for testing."""
        self.auth = DefaultJWTAuthentication()

    def test_create_models_if_not_exists(self):
        """
        Test the create_models_if_not_exists method.

        Ensures that the models' tables are created in the database when they don't exist.
        """
        with patch('lightapi.auth.Base.metadata.create_all') as mock_create_all:
            self.auth.create_models_if_not_exists()
            mock_create_all.assert_called_once()


class TestValidToken(unittest.TestCase):
    def setUp(self):
        self.jwt_auth = DefaultJWTAuthentication()

    def test_authenticate_valid_token(self):
        """
        Test that a valid JWT token returns the correct user information.

        This test mocks a valid JWT token and ensures that the `authenticate` method
        returns the expected user information dictionary with the correct user ID and
        username. The mock user object has specific attributes to simulate a successful
        authentication process.
        """
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'test_user'

        with patch('lightapi.auth.jwt.decode', return_value={'user_id': 1}), \
                patch('lightapi.auth.SessionLocal') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter_by.return_value.first.return_value = mock_user

            user_info = self.jwt_auth.authenticate('valid.jwt.token')

            self.assertEqual(user_info, {'user_id': 1, 'username': 'test_user'})


class TestInvalidToken(unittest.TestCase):
    def setUp(self):
        self.jwt_auth = DefaultJWTAuthentication()

    def test_authenticate_invalid_token(self):
        """
        Test that an invalid JWT token raises an HTTPUnauthorized exception.

        This test mocks the behavior where the JWT token is invalid and ensures that
        the `authenticate` method raises an `HTTPUnauthorized` exception as expected.
        """
        token = 'invalid.jwt.token'
        with patch('lightapi.auth.jwt.decode', side_effect=jwt.InvalidTokenError), \
             patch('lightapi.auth.SessionLocal'):
            with self.assertRaises(web.HTTPUnauthorized):
                self.jwt_auth.authenticate(token)


class TestExpiredToken(unittest.TestCase):
    def setUp(self):
        self.jwt_auth = DefaultJWTAuthentication()

    def test_authenticate_expired_token(self):
        """
        Test that an expired JWT token raises an HTTPUnauthorized exception.

        This test simulates an expired JWT token and verifies that the `authenticate`
        method raises an `HTTPUnauthorized` exception due to the expired signature.
        """
        token = 'expired.jwt.token'
        with patch('lightapi.auth.jwt.decode', side_effect=jwt.ExpiredSignatureError), \
             patch('lightapi.auth.SessionLocal'):
            with self.assertRaises(web.HTTPUnauthorized):
                self.jwt_auth.authenticate(token)


class TestUserNotFound(unittest.TestCase):
    def setUp(self):
        self.jwt_auth = DefaultJWTAuthentication()

    def test_authenticate_user_not_found(self):
        """
        Test that if the user is not found in the database, the method returns None.

        This test mocks a valid JWT token but simulates a scenario where the user is
        not found in the database. It ensures that the `authenticate` method returns
        `None` when no user is found.
        """
        payload = {'user_id': 1}
        token = 'valid.jwt.token'

        with patch('lightapi.auth.jwt.decode', return_value=payload), \
             patch('lightapi.auth.SessionLocal') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter_by.return_value.first.return_value = None

            user_info = self.jwt_auth.authenticate(token)

            self.assertIsNone(user_info)


if __name__ == '__main__':
    unittest.main()

