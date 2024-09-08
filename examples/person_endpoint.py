from lightapi import LightApi
from lightapi.database import Base

from sqlalchemy import Column, String, Boolean

from lightapi.rest import RestEndpoint


class Person(Base):
    name = Column(String)
    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)

    def serialize(self) -> dict:
        data = super().serialize()
        return {'data': data}


class Company(Base):
    name = Column(String)
    email = Column(String, unique=True)
    website = Column(String)


class MyCustomEndpoint(RestEndpoint):
    def get(self):
        return {'data': 'Hello World'}


if __name__ == '__main__':
    app = LightApi()
    app.register(
        {
            '/company': Company,
            '/person': Person
        }
    )
    app.register({'/custom': MyCustomEndpoint})
    app.run()

