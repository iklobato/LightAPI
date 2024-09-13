from lightapi import LightApi
from lightapi.database import Base

from sqlalchemy import Column, String, Boolean


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


if __name__ == '__main__':

    def initialize(**kwargs):
        print(f'My pre configuration with {kwargs} parameters')

    app = LightApi(
        initialize_callback=initialize,
        initialize_arguments={'param1': 'value1'}
    )
    app.register({
        '/company': Company,
        '/person': Person,
    })
    app.run()

