from lightapi import LightApi

from lightapi.rest import RestEndpoint


class CustomEndpoint(RestEndpoint):
    http_method_names = ['GET', 'POST']
    tablename = 'custom'

    def get(self, request):
        return {'message': 'GET'}

    def post(self, request):
        return {'message': 'POST'}


if __name__ == '__main__':

    def initialize(**kwargs):
        print(f'My pre configuration with {kwargs} parameters')

    app = LightApi(
        initialize_callback=initialize,
        initialize_arguments={'param1': 'value1'}
    )
    app.register({
        '/custom': CustomEndpoint
    })
    app.run()

