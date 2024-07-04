from sqlalchemy import Column, Integer, String
from database import CustomBase
from lightapi import LightApi
import os



class Person(CustomBase):
    name = Column(String(255))
    email = Column(String(255), unique=True)
    #id column already registered as primary key and integer




if __name__ == '__main__':

    app = LightApi()
    app.register({'/person': Person})
    app.run()