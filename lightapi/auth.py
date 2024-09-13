from abc import ABC, abstractmethod
import jwt
from typing import Dict, Optional, Union, Type
from aiohttp import web
import datetime
import os

from lightapi.database import SessionLocal, Base, engine
from lightapi.models import User, JWTToken


class AbstractAuthentication(ABC):
    """
    An abstract base class for authentication mechanisms in the LightApi application.

    This class defines the core methods and properties that any authentication class should implement.

    Methods:
        authenticate(token: str) -> Optional[Dict[str, str]]:
            Authenticates the provided token and returns user information if valid.

        generate_token(user_info: Dict[str, str]) -> str:
            Generates a new token for the given user information.

    Attributes:
        SECRET_KEY (str): The secret key used for token encoding/decoding. This should be overridden
                          by subclasses to set a specific secret key for the authentication mechanism.
    """

    SECRET_KEY: str

    def __init__(self, user_model: Optional[Type] = None, token_model: Optional[Type] = None):
        """
        Initializes the AbstractAuthentication class with optional user and token models.
        If the tables for these models don't exist in the database, they will be created.

        Args:
            user_model (Optional[Type]): The user model to be used for authentication.
            token_model (Optional[Type]): The token model to be used for JWT operations.
        """
        self._user_model = user_model or self.get_user_model()
        self._token_model = token_model or self.get_token_model()

        # Automatically create tables for the models if they don't exist
        self.create_models_if_not_exists()

    def create_models_if_not_exists(self):
        """
        Creates the necessary tables for the user and token models if they don't exist in the database.
        """
        Base.metadata.create_all(
            bind=engine, tables=[
                self._user_model.__table__,
                self._token_model.__table__
            ]
        )

    @abstractmethod
    def authenticate(self, token: str):
        """
        Authenticates the provided token and returns user information if the token is valid.

        Args:
            token (str): The token to be authenticated.

        Returns:
            Optional[Dict[str, str]]: A dictionary with user information if authentication is successful,
                                       otherwise None.

        Example:
            auth = SomeAuthenticationClass()
            user_info = auth.authenticate('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIn0.S2k4d8iIWT7Dw23kP_1GFGK7eC8mlM5LdrVoOcOXU74')
            if user_info:
                print(f"Authenticated User Info: {user_info}")
            else:
                print("Authentication failed.")
        """
        return NotImplementedError(
            f'{self.__class__.__name__} must implement authenticate method'
        )

    # @abstractmethod
    # def generate_token(self, user_info: Dict[str, str]):
    #     """
    #     Generates a new token for the provided user information.
    #
    #     Args:
    #         user_info (Dict[str, str]): A dictionary containing user information to be encoded in the token.
    #
    #     Returns:
    #         str: The generated token.
    #
    #     Example:
    #         auth = SomeAuthenticationClass()
    #         token = auth.generate_token({'user_id': '123'})
    #         print(f"Generated JWTToken: {token}")
    #     """
    #     return NotImplementedError(
    #         f'{self.__class__.__name__} must implement generate_token method'
    #     )

    @abstractmethod
    def get_user_model(self):
        """
        Returns the SQLAlchemy model class for the user.

        This method should be overridden by subclasses to return the appropriate user model.

        Returns:
            Type: The SQLAlchemy model class for the user.

        Example:
            class MyAuthentication(AbstractAuthentication):
                def get_user_model(self):
                    return MyUserModel
        """
        return NotImplementedError(
            f'{self.__class__.__name__}'
        )

    @abstractmethod
    def get_token_model(self):
        """
        Returns the SQLAlchemy model class for the token.

        This method should be overridden by subclasses to return the appropriate token model.

        Returns:
            Type: The SQLAlchemy model class for the token.

        Example:
            class MyAuthentication(AbstractAuthentication):
                def get_token_model(self):
                    return MyJWTTokenModel
        """
        return NotImplementedError(
            f'{self.__class__.__name__}'
        )


class DefaultJWTAuthentication(AbstractAuthentication):
    """
    Default JWT authentication handler using the `pyjwt` library.

    This class handles creating and validating JWT tokens with a dynamically generated
    secret key on each run. It can be used to secure REST APIs by embedding user
    information inside a JWT and verifying it in subsequent requests.

    Attributes:
        ALGORITHM (str): The algorithm used for encoding and decoding the JWT.
        EXPIRATION_DELTA (datetime.timedelta): The time duration after which the token expires.

    Usage example:


        jwt_auth = DefaultJWTAuthentication()


        token = jwt_auth.encode_token('user123')
        print(f"Generated JWTToken: {token}")


        try:
            payload = jwt_auth.decode_token(token)
            print(f"Decoded Payload: {payload}")
        except web.HTTPUnauthorized as e:
            print(f"Invalid or expired token: {str(e)}")


        async def some_protected_endpoint(request):
            user_info = await jwt_auth.authenticate_request(request)
            return web.json_response({"message": "Authenticated", "user": user_info})
    """

    ALGORITHM = "HS256"
    EXPIRATION_DELTA = datetime.timedelta(hours=1)

    def __init__(
            self,
            algorithm: str = "HS256",
            expiration_delta: datetime.timedelta = None,
            user_model: Optional[Type] = None,
            token_model: Optional[Type] = None
    ):
        """
        Initializes the DefaultJWT authentication handler with optional models and configurations.

        Args:
            algorithm (str): The algorithm used for JWT encoding/decoding.
            expiration_delta (datetime.timedelta): The time duration after which the token expires.
            user_model (Optional[Type]): Custom user model.
            token_model (Optional[Type]): Custom token model.
        """
        super().__init__(user_model=user_model, token_model=token_model)
        self.ALGORITHM = algorithm
        self.EXPIRATION_DELTA = expiration_delta or self.EXPIRATION_DELTA
        self._secret_key: Optional[str] = None

    @property
    def secret_key(self) -> str:
        """
        Generates and returns a unique secret key for JWT encoding and decoding.

        If no secret key has been generated yet, this method will create a random 32-byte
        hexadecimal string and store it. This key will be used for all token operations
        within the application run.

        Returns:
            str: A unique secret key for the current application run.

        Example:
            jwt_auth = DefaultJWTAuthentication()
            print(f"Secret Key: {jwt_auth.secret_key}")
        """
        if self._secret_key is None:
            self._secret_key = os.urandom(32).hex()
        return self._secret_key

    def encode_token(self, user_id: str) -> str:
        """
        Encodes a JWT token for a given user ID.

        The token will contain the user ID as payload and will be valid until the expiration
        time defined by `EXPIRATION_DELTA`.

        Args:
            user_id (str): The unique identifier for the user (e.g., username or user ID).

        Returns:
            str: The JWT token encoded with the user's ID.

        Example:
            jwt_auth = DefaultJWTAuthentication()
            token = jwt_auth.encode_token('user123')
            print(f"Generated JWTToken: {token}")
        """
        payload = {
            'user_id': user_id,
            'exp': (datetime.datetime.utcnow() + self.EXPIRATION_DELTA).timestamp()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

        with SessionLocal() as session:
            db_token = self._token_model(user_id=user_id, token=token)
            session.add(db_token)
            session.commit()

        return token

    def decode_token(self, token: str) -> Union[Dict, None]:
        """
        Decodes and verifies a JWT token.

        This method will attempt to decode the token using the current `secret_key`. If the
        token is invalid or expired, it will raise an `HTTPUnauthorized` exception.

        Args:
            token (str): The JWT token to decode.

        Returns:
            Dict: The decoded token payload if valid.

        Raises:
            web.HTTPUnauthorized: If the token is expired or invalid.

        Example:
            jwt_auth = DefaultJWTAuthentication()
            try:
                payload = jwt_auth.decode_token(token)
                print(f"Decoded Payload: {payload}")
            except web.HTTPUnauthorized as e:
                print(f"Invalid or expired token: {str(e)}")
        """
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])

            with SessionLocal() as session:
                db_token = session.query(JWTToken).filter(JWTToken.token == token).first()
                if not db_token:
                    raise web.HTTPUnauthorized(reason="Invalid token.")

            return decoded
        except jwt.ExpiredSignatureError:
            raise web.HTTPUnauthorized(reason="Token has expired.")
        except jwt.InvalidTokenError:
            raise web.HTTPUnauthorized(reason="Invalid token.")

    def authenticate(self, token: str) -> Optional[Dict[str, str]]:
        """
        Authenticates the provided JWT token and returns user information if valid.

        Args:
            token (str): The JWT token to be authenticated.

        Returns:
            Optional[Dict[str, str]]: A dictionary with user information if the token is valid,
                                       otherwise None.

        Example:
            jwt_auth = DefaultJWTAuthentication()
            user_info = jwt_auth.authenticate(token)
            if user_info:
                print(f"Authenticated User Info: {user_info}")
            else:
                print("Authentication failed.")
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])
            user_id = payload.get('user_id')

            with SessionLocal() as session:
                user = session.query(self._user_model).filter_by(pk=user_id).first()

                if user:
                    return {'user_id': user.id, 'username': user.username}
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise web.HTTPUnauthorized(reason="Invalid or expired token.")

        return None

    # def generate_token(self, user_info: Dict[str, str]) -> str:
    #     """
    #     Generates a JWT token for the provided user information and stores it in the database.
    #
    #     Args:
    #         user_info (Dict[str, str]): A dictionary containing user information to be included in the token.
    #
    #     Returns:
    #         str: The generated JWT token.
    #
    #     Example:
    #         jwt_auth = DefaultJWTAuthentication()
    #         token = jwt_auth.generate_token({'user_id': '123'})
    #         print(f"Generated JWTToken: {token}")
    #     """
    #     payload = {
    #         **user_info,
    #         'exp': datetime.datetime.utcnow() + self.EXPIRATION_DELTA,
    #     }
    #     token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
    #
    #     with SessionLocal() as session:
    #         db_token = JWTToken()
    #         db_token.token = token
    #         db_token.user_id = user_info.get('user_id')
    #         session.add(db_token)
    #         session.commit()
    #
    #     return token

    def get_user_model(self):
        return User

    def get_token_model(self):
        return JWTToken
