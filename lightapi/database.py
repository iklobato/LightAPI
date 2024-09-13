import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lightapi.db")

is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite://")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@as_declarative()
class Base:
    """
    Base class for SQLAlchemy models with automatic table naming and serialization.

    This class provides the following features for all SQLAlchemy models that inherit from it:

    - Automatic table name generation based on the class name.
    - Serialization of model instances to dictionaries.

    Attributes:
        pk (Column): Primary key column for derived models. Automatically generated.

    Methods:
        __tablename__(cls):
            Generates a table name based on the class name, converted to lowercase.

            Returns:
                str: The table name derived from the class name.

        serialize(self) -> dict:
            Serializes the model instance into a dictionary with column names as keys.

            Returns:
                dict: A dictionary where keys are column names and values are column data.

    Example:
        Define a model inheriting from `Base`:

        ```python
        class User(Base):
            __tablename__ = 'users'
            username = Column(String, index=True)
            email = Column(String, index=True)
        ```

        Create and serialize an instance of `User`:

        ```python
        user = User(username='john_doe', email='john@example.com')
        user_dict = user.serialize()
        print(user_dict)
        # Output: {'username': 'john_doe', 'email': 'john@example.com'}
        ```
    """

    pk = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    __table__ = None

    @property
    def table(self):
        """
        Returns the SQLAlchemy table associated with this model.

        Returns:
            Table: The SQLAlchemy Table object for the model.
        """
        return self.__table__

    @declared_attr
    def __tablename__(cls):
        """
        Automatically generates the table name from the class name.

        The table name is derived by converting the class name to lowercase.

        Returns:
            str: The generated table name based on the class name.
        """
        return cls.__name__.lower()

    def serialize(self) -> dict:
        """
        Serializes the model instance into a dictionary.

        Converts the model instance into a dictionary where each key corresponds to a column name,
        and each value is the data stored in that column.

        Returns:
            dict: A dictionary representation of the model instance with column names as keys and column values as values.
        """
        return {
            column.name: getattr(self, column.name) for column in self.table.columns
        }
