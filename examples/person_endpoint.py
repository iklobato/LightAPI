from lightapi import LightApi
from models import Person, Company


if __name__ == '__main__':
    app = LightApi()
    app.register({'/person': Person})
    app.register({'/company': Company})
    app.run()
