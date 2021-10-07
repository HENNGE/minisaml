import base64
import datetime
from dataclasses import dataclass
from typing import Collection, Dict, Iterable, List, Optional, Union

from cryptography.x509 import Certificate
from lxml.etree import QName, _Element as Element
from minisignxml.config import VerifyConfig
from minisignxml.errors import ElementNotFound
from minisignxml.verify import extract_verified_element_and_certificate

from .errors import (
    AudienceMismatch,
    MalformedSAMLResponse,
    ResponseExpired,
    ResponseTooEarly,
)
from .internal.constants import *
from .internal.namespaces import NAMESPACE_MAP
from .internal.saml import saml_to_datetime
from .internal.utils import find_or_raise


@dataclass(frozen=True)
class Attribute:
    name: str
    values: List[str]
    format: Optional[str]
    extra_attributes: Dict[str, str]

    @property
    def value(self) -> Optional[str]:
        return self.values[0] if self.values else None


@dataclass(frozen=True)
class Response:
    issuer: str
    name_id: str
    audience: str
    attributes: List[Attribute]
    session_not_on_or_after: Optional[datetime.datetime]
    in_response_to: Optional[str]
    certificate: Certificate

    @property
    def attrs(self) -> Dict[str, Optional[str]]:
        return {attr.name: attr.value for attr in self.attributes}


def validate_response(
    *,
    data: Union[bytes, str],
    certificate: Union[Certificate, Collection[Certificate]],
    expected_audience: str,
    signature_verification_config: VerifyConfig = VerifyConfig.default()
) -> Response:
    xml = base64.b64decode(data)
    certificates: Collection[Certificate]
    if isinstance(certificate, Certificate):
        certificates = {certificate}
    else:
        certificates = certificate
    element, certificate_used = extract_verified_element_and_certificate(
        xml=xml, certificates=certificates, config=signature_verification_config
    )
    if element.tag == QName(NAMES_SAML2_PROTOCOL, "Response"):
        assertion = find_or_raise(element, "./saml:Assertion")
    elif element.tag == QName(NAMES_SAML2_ASSERTION, "Assertion"):
        assertion = element
    else:
        raise MalformedSAMLResponse(
            "Signed element is neither a Response with an Assertion, nor an Assertion"
        )
    issuer = find_or_raise(assertion, "./saml:Issuer").text
    subject = find_or_raise(assertion, "./saml:Subject")
    name_id = find_or_raise(subject, "./saml:NameID").text
    subject_confirmation_method = find_or_raise(subject, "./saml:SubjectConfirmation")
    subject_confirmation_data = find_or_raise(
        subject_confirmation_method, "./saml:SubjectConfirmationData"
    )
    in_response_to = subject_confirmation_data.attrib.get("InResponseTo", None)
    conditions = find_or_raise(assertion, "./saml:Conditions")
    not_before = saml_to_datetime(conditions.attrib["NotBefore"])
    not_on_or_after = saml_to_datetime(conditions.attrib["NotOnOrAfter"])
    now = datetime.datetime.utcnow()
    if now < not_before:
        raise ResponseTooEarly()
    if now >= not_on_or_after:
        raise ResponseExpired()

    audience = find_or_raise(
        conditions, "./saml:AudienceRestriction/saml:Audience"
    ).text

    if audience != expected_audience:
        raise AudienceMismatch(
            received_audience=audience, expected_audience=expected_audience
        )

    raw_session_not_on_or_after = find_or_raise(
        assertion, "./saml:AuthnStatement"
    ).attrib.get("SessionNotOnOrAfter", None)

    session_not_on_or_after = raw_session_not_on_or_after and saml_to_datetime(
        raw_session_not_on_or_after
    )

    try:
        attribute_statement = find_or_raise(assertion, "./saml:AttributeStatement")
    except ElementNotFound:
        attribute_statement = None

    attributes = (
        list(gather_attributes(attribute_statement))
        if attribute_statement is not None
        else []
    )

    return Response(
        issuer=issuer,
        name_id=name_id,
        audience=audience,
        attributes=attributes,
        session_not_on_or_after=session_not_on_or_after,
        in_response_to=in_response_to,
        certificate=certificate_used,
    )


def gather_attributes(attribute_statement: Element) -> Iterable[Attribute]:
    for attribute in attribute_statement.findall("./saml:Attribute", NAMESPACE_MAP):
        values = [
            value.text
            for value in attribute.findall("./saml:AttributeValue", NAMESPACE_MAP)
        ]
        extra_attributes = {k: v for k, v in attribute.attrib.items()}
        name = extra_attributes.pop("Name")
        format = extra_attributes.pop("NameFormat", None)
        yield Attribute(
            name=name,
            values=values,
            format=format,
            extra_attributes=extra_attributes,
        )
