from sqlalchemy import Boolean, Column, String

from lightapi import LightApi
from lightapi.database import Base


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
    app = LightApi()
    app.register({'/person': Person})
    app.register({'/company': Company})
    app.run()

