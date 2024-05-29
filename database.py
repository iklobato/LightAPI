import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, as_declarative
from sqlalchemy.orm import sessionmaker, declared_attr

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lightapi.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@as_declarative()
class CustomBase:
    def __init__(self):
        self.__table__ = None

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
