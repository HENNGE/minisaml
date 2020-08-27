import datetime

from minisignxml.internal.utils import serialize_xml

from .constants import *
from .namespaces import saml, samlp


def datetime_to_saml(t: datetime.datetime) -> str:
    return t.strftime(DATE_TIME_FORMAT)


def saml_to_datetime(s: str) -> datetime.datetime:
    if "." in s:
        return datetime.datetime.strptime(s, DATE_TIME_FORMAT_FRACTIONAL)
    return datetime.datetime.strptime(s, DATE_TIME_FORMAT)


def build_saml_request(
    issuer: str, acs_url: str, request_id: str, force_reauthentication: bool
) -> bytes:
    request = samlp.AuthnRequest(
        saml.Issuer(issuer),
        samlp.NameIDPolicy(Format=NAMEID_FORMAT_UNSPECIFIED),
        ID=request_id,
        Version="2.0",
        IssueInstant=datetime_to_saml(datetime.datetime.utcnow()),
        ProtocolBinding=BINDINGS_HTTP_POST,
        AssertionConsumerServiceURL=acs_url,
    )
    if force_reauthentication:
        request.set("ForceAuthn", "true")
    return serialize_xml(request)
