from sqlalchemy import Column, Integer, String, Boolean

from lightapi.database import Base


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
