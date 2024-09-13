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
        """
        Custom initialization function called before the LightApi application starts.

        This function is used to perform any setup or configuration tasks that need to
        occur before the application begins running. It allows for flexibility by accepting
        arbitrary keyword arguments, which can be used to pass configuration values or
        parameters required for initialization.

        Example usage:
        --------------
        initialize(param1='value1', param2='value2')

        Args:
            **kwargs: Arbitrary keyword arguments that can be used to pass configuration
                      parameters or other values needed during the initialization phase.

        Returns:
            None
        """
        print(f'My pre-configuration with {kwargs} parameters')

    app = LightApi(
        initialize_callback=initialize,
        initialize_arguments={'param1': 'value1'}
    )
    app.register({
        '/custom': CustomEndpoint
    })
    app.run()

