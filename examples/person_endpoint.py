from sqlalchemy import Column, Integer, String
from database import CustomBase
from lightapi import LightApi


class Person(CustomBase):
    pk = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String)
    email = Column(String, unique=True)


if __name__ == '__main__':

    app = LightApi()
    app.register({'/person': Person})
    app.run()
