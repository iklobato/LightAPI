import unittest
from unittest.mock import patch
from lightapi.models import Token
from lightapi.auth import DefaultJWTAuthentication


class TestEncodeToken(unittest.TestCase):
    @patch('jwt.encode')
    @patch('lightapi.database.SessionLocal')
    def test_encode_token(self, mock_session, mock_jwt_encode):
        jwt_auth = DefaultJWTAuthentication()
        mock_jwt_encode.return_value = 'mock_token'
        user_id = 'user123'

        token = jwt_auth.encode_token(user_id)

        self.assertEqual(token, 'mock_token')
        mock_jwt_encode.assert_called_once()
        self.assertEqual(mock_jwt_encode.call_args[0][0]['user_id'], user_id)

        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = Token()
        with mock_session.return_value as session:
            db_token = session.query(Token).filter(Token.token == 'mock_token').first()
            self.assertIsNotNone(db_token)


class TestDecodeToken(unittest.TestCase):
    @patch('jwt.decode')
    @patch('lightapi.database.SessionLocal')
    def test_decode_token(self, mock_session, mock_jwt_decode):
        jwt_auth = DefaultJWTAuthentication()
        mock_jwt_decode.return_value = {'user_id': 'user123'}
        token = 'mock_token'

        with patch('lightapi.database.SessionLocal') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = Token()
            payload = jwt_auth.decode_token(token)

        self.assertEqual(payload, {'user_id': 'user123'})
        mock_jwt_decode.assert_called_once_with(token, jwt_auth.secret_key, algorithms=[jwt_auth.ALGORITHM])


class TestAuthenticate(unittest.TestCase):
    @patch('jwt.decode')
    @patch('lightapi.database.SessionLocal')
    def test_authenticate(self, mock_session, mock_jwt_decode):
        jwt_auth = DefaultJWTAuthentication()
        mock_jwt_decode.return_value = {'user_id': 'user123'}
        token = 'mock_token'

        with patch('lightapi.database.SessionLocal') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = Token()
            user_info = jwt_auth.authenticate(token)

        self.assertEqual(user_info, {'user_id': 'user123'})
        mock_jwt_decode.assert_called_once_with(token, jwt_auth.secret_key, algorithms=[jwt_auth.ALGORITHM])


class TestGenerateToken(unittest.TestCase):
    @patch('jwt.encode')
    @patch('lightapi.database.SessionLocal')
    def test_generate_token(self, mock_session, mock_jwt_encode):
        jwt_auth = DefaultJWTAuthentication()
        mock_jwt_encode.return_value = 'mock_token'
        user_info = {'user_id': '123'}

        token = jwt_auth.generate_token(user_info)

        self.assertEqual(token, 'mock_token')
        mock_jwt_encode.assert_called_once()
        self.assertEqual(mock_jwt_encode.call_args[0][0]['user_id'], '123')

        mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = Token()
        with mock_session.return_value as session:
            db_token = session.query(Token).filter(Token.token == 'mock_token').first()
            self.assertIsNotNone(db_token)


if __name__ == '__main__':
    unittest.main()
