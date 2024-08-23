from lightapi.lightapi import LightApi


def test_app_initialization():
    """
   Test if the LightApi application is initialized properly.

   Creates an instance of LightApi and checks that the `app` attribute is not `None`.
   This ensures that the application instance has been created successfully.

    """
    api = LightApi()
    assert api.app is not None


def test_app_logging():
    """
    Test the logging configuration of the application.

    Retrieves the global logger and checks that its logging level is set to `INFO`.
    This ensures that the logging configuration is set up correctly to capture informational messages.

    """
    import logging
    logger = logging.getLogger()
    assert logger.level == logging.INFO


def test_app_routes_registration():
    """
    Test if routes are registered with the application.

    Creates an instance of LightApi and checks that there are registered routes in the application's router.
    This ensures that the route registration process has occurred and at least one route is available.

    """
    api = LightApi()
    assert len(api.app.router.routes()) > 0