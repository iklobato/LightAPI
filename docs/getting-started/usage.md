---
title: Usage
---

Here’s a quick example of how to use LightAPI.


``` python
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

```python
from lightapi.rest import RestEndpoint

class UserEndpoint(RestEndpoint):
    http_method_names = ['GET', 'POST']  # Allow GET and POST methods only

    def get(self, request):
        return {
            'message': 'Hello, World!'
        }
    
    def post(self, request):
        return {
            'message': 'Hello, World!'
        }

```
On this example we have created a custom endpoint that only allows GET and POST methods.
Here we do not depend on the model, so we can return any data we want.