---
title: Usage
---

Here’s a quick example of how to use LightAPI.

!!! tip ""
    ``` py
    from sqlalchemy import Column, Integer, String, Boolean
    from lightapi import LightApi
    from lightapi.database import Base

    class Person(Base):
        name = Column(String)
        email = Column(String, unique=True)
        email_verified = Column(Boolean, default=False)

    if __name__ == '__main__':
        app = LightApi()
        app.register({'/person': Person})
        app.run()
    ```

Once this is set up, LightAPI will automatically create CRUD endpoints for the `Person` model.

