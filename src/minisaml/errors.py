class MiniSAMLError(Exception):
    pass


class MalformedSAMLResponse(MiniSAMLError):
    pass


class ResponseExpired(MiniSAMLError):
    pass


class ResponseTooEarly(MiniSAMLError):
    pass
