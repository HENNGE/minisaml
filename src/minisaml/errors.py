import datetime
from dataclasses import dataclass


class MiniSAMLError(Exception):
    pass


class MalformedSAMLResponse(MiniSAMLError):
    pass


@dataclass
class ResponseExpired(MiniSAMLError):
    observed_time: datetime.datetime
    not_on_or_after: datetime.datetime


@dataclass
class ResponseTooEarly(MiniSAMLError):
    observed_time: datetime.datetime
    not_before: datetime.datetime


@dataclass
class AudienceMismatch(MiniSAMLError):
    received_audience: str
    expected_audience: str


@dataclass
class IssuerMismatch(MiniSAMLError):
    received_issuer: str
    expected_issuer: str
