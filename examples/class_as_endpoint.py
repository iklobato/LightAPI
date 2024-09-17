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

    app = LightApi()
    app.register({
        '/custom': CustomEndpoint
    })
    app.run()

