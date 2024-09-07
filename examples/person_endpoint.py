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

class Customer(Base):
    name = Column(String)
    email = Column(String, unique=True)
    address = Column(String)

if __name__ == '__main__':
    app = LightApi()
    # creates the API endpoints with the given keys
    app.register({"person": Person, "company": Company})
    # creates an API endpoint corresponding to the model name -> 'customer'
    app.register({"": Customer})

    app.run()

