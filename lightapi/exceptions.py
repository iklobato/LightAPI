class MissingHandlerImplementationError(Exception):
    """
    Raised when a subclass does not implement the required handler for a specified HTTP verb.
    """

    def __init__(self, handler_name: str, verb: str) -> None:
        super().__init__(
            f"Missing implementation for {handler_name} required for HTTP verb: {verb}. "
            f"Please implement this handler in the subclass."
        )
