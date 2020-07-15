class MiniSAMLError(Exception):
    pass


class MalformedSAMLResponse(MiniSAMLError):
    pass


class ResponseExpired(MiniSAMLError):
    pass


class ResponseTooEarly(MiniSAMLError):
    pass


class AudienceMismatch(MiniSAMLError):
    def __init__(self, *, received_audience: str, expected_audience: str):
        self.received_audience = received_audience
        self.expected_audience = expected_audience
        super().__init__()
