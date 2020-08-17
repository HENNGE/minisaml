import base64
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from cryptography.x509 import Certificate
from lxml.etree import QName
from minisignxml.config import VerifyConfig
from minisignxml.errors import ElementNotFound
from minisignxml.verify import extract_verified_element

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
    value: str
    format: Optional[str]
    extra_attributes: Dict[str, str]


@dataclass(frozen=True)
class Response:
    issuer: str
    name_id: str
    audience: str
    attributes: List[Attribute]
    session_not_on_or_after: Optional[datetime.datetime]
    in_response_to: Optional[str]

    @property
    def attrs(self) -> Dict[str, str]:
        return {attr.name: attr.value for attr in self.attributes}


def validate_response(
    *,
    data: Union[bytes, str],
    certificate: Certificate,
    expected_audience: str,
    signature_verification_config: VerifyConfig = VerifyConfig.default()
) -> Response:
    xml = base64.b64decode(data)
    element = extract_verified_element(
        xml=xml, certificate=certificate, config=signature_verification_config
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
        attributes = []
        for attribute in attribute_statement.findall("./saml:Attribute", NAMESPACE_MAP):
            value = find_or_raise(attribute, "./saml:AttributeValue").text
            extra_attributes = {k: v for k, v in attribute.attrib.items()}
            name = extra_attributes.pop("Name")
            format = extra_attributes.pop("NameFormat", None)
            attributes.append(
                Attribute(
                    name=name,
                    value=value,
                    format=format,
                    extra_attributes=extra_attributes,
                )
            )
    except ElementNotFound:
        attributes = []

    return Response(
        issuer=issuer,
        name_id=name_id,
        audience=audience,
        attributes=attributes,
        session_not_on_or_after=session_not_on_or_after,
        in_response_to=in_response_to,
    )
