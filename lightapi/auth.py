from abc import ABC, abstractmethod
import jwt
from typing import Dict, Optional, Union, Type
from aiohttp import web
import datetime
import os


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

    @abstractmethod
    def authenticate(self, token: str) -> Type[NotImplementedError, Optional[Dict[str, str]]]:
        """
        Authenticates the provided token and returns user information if the token is valid.

        Args:
            token (str): The token to be authenticated.

        Returns:
            Optional[Dict[str, str]]: A dictionary with user information if authentication is successful,
                                       otherwise None.
        """
        return NotImplementedError

    @abstractmethod
    def generate_token(self, user_info: Dict[str, str]) -> Type[NotImplementedError, str]:
        """
        Generates a new token for the provided user information.

        Args:
            user_info (Dict[str, str]): A dictionary containing user information to be encoded in the token.

        Returns:
            str: The generated token.
        """
        return NotImplementedError


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

        # Creating a JWT instance
        jwt_auth = DefaultJWT()

        # Encoding a token for a user with ID 'user123'
        token = jwt_auth.encode_token('user123')
        print(f"Generated Token: {token}")

        # Decoding a token to verify its validity
        try:
            payload = jwt_auth.decode_token(token)
            print(f"Decoded Payload: {payload}")
        except web.HTTPUnauthorized as e:
            print(f"Invalid or expired token: {str(e)}")

        # Authenticating an HTTP request (assuming aiohttp request)
        async def some_protected_endpoint(request):
            user_info = await jwt_auth.authenticate_request(request)
            return web.json_response({"message": "Authenticated", "user": user_info})

    """

    ALGORITHM = "HS256"
    EXPIRATION_DELTA = datetime.timedelta(hours=1)

    def __init__(self) -> None:
        """
        Initializes the DefaultJWT authentication handler.

        The `secret_key` is generated dynamically upon the first access and
        remains constant for the duration of the application run.
        """
        self._secret_key: Optional[str] = None  # Lazily initialized secret key

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
            jwt_auth = DefaultJWT()
            print(f"Secret Key: {jwt_auth.secret_key}")
        """
        if self._secret_key is None:
            self._secret_key = os.urandom(32).hex()  # Generate random 32-byte key
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
            jwt_auth = DefaultJWT()
            token = jwt_auth.encode_token('user123')
            print(f"Generated Token: {token}")
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + self.EXPIRATION_DELTA
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

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
            jwt_auth = DefaultJWT()
            try:
                payload = jwt_auth.decode_token(token)
                print(f"Decoded Payload: {payload}")
            except web.HTTPUnauthorized as e:
                print(f"Invalid or expired token: {str(e)}")
        """
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])
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
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            # Handle expired token
            return None
        except jwt.InvalidTokenError:
            # Handle invalid token
            return None

    def generate_token(self, user_info: Dict[str, str]) -> str:
        """
        Generates a new JWT token for the provided user information.

        Args:
            user_info (Dict[str, str]): A dictionary containing user information to be encoded in the token.

        Returns:
            str: The generated JWT token.
        """
        payload = {
            **user_info,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiry
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
