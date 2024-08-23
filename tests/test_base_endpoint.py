from lightapi.base_endpoint import GetRequestHandlerStrategy, PostRequestHandlerStrategy


class MockEndpoint:
    def get(self):
        return {"message": "GET was a successful!"}

    def post(self):
        return {"message": "POST was a successful!"}


def test_get_request():
    """
    Tests the GET request handler to ensure it returns the correct response
    when the endpoint responds successfully.

    """

    strategy = GetRequestHandlerStrategy()
    response = strategy.handle(None, MockEndpoint())
    assert response == '{"message": "GET was a successful!"}'


def test_post_request():
    """
    Tests the GET request handler to ensure it returns the correct response
    when the endpoint responds successfully.

    """
    strategy = PostRequestHandlerStrategy()
    response = strategy.handle(None, MockEndpoint())
    assert response == '{"message": "POST was a successful"}'


def test_get_request_error():
    """
    Tests the GET request handler to ensure it returns the correct response
    when the endpoint responds successfully.

    """

    class MockEndpointWithError:
        def get(self):
            raise Exception("Error")

    strategy = GetRequestHandlerStrategy()
    response = strategy.handle(None, MockEndpointWithError())
    assert response == '{"error": "Internal server error!"}'


def test_post_request_error():
    """
    Tests the GET request handler to ensure it returns the correct response
    when the endpoint responds successfully.

    """

    class MockEndpointWithError:
        def post(self):
            raise Exception("Error")

    strategy = PostRequestHandlerStrategy()
    response = strategy.handle(None, MockEndpointWithError())
    assert response == '{"error": "Internal server error!"}'
