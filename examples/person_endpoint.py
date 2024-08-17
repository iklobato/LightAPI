from lightapi import LightApi
from database import Base

from sqlalchemy import Column, Integer, String, Boolean


class Person(Base):
    __tablename__ = "person"

    pk = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)

    def as_dict(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "email": self.email,
            "email_verified": self.email_verified,
        }


class Company(Base):
    __tablename__ = "company"

    pk = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    website = Column(String)

    def as_dict(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "email": self.email,
            "website": self.website,
        }


if __name__ == '__main__':
    app = LightApi()
    app.register({'/person': Person})
    app.register({'/company': Company})
    app.run()
