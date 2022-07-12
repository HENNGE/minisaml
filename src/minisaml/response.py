import asyncio
import base64
import datetime
from dataclasses import dataclass
from typing import (
    Awaitable,
    Callable,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from cryptography.x509 import Certificate
from lxml.etree import QName
from lxml.etree import _Element as Element
from minisignxml.config import VerifyConfig
from minisignxml.errors import ElementNotFound
from minisignxml.internal import utils
from minisignxml.verify import extract_verified_element_and_certificate

from .errors import (
    AudienceMismatch,
    IssuerMismatch,
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


@dataclass(frozen=True)
class TimeDriftLimits:
    not_before_max_drift: datetime.timedelta
    not_on_or_after_max_drift: datetime.timedelta

    @classmethod
    def none(cls) -> "TimeDriftLimits":
        return cls(
            not_before_max_drift=datetime.timedelta(),
            not_on_or_after_max_drift=datetime.timedelta(),
        )


@dataclass(frozen=True)
class ValidationConfig:
    certificate: Union[Certificate, Collection[Certificate]]
    signature_verification_config: VerifyConfig = VerifyConfig.default()
    allowed_time_drift: TimeDriftLimits = TimeDriftLimits.none()


State = TypeVar("State")

SyncGetConfigForIssuer = Callable[[str], Tuple[ValidationConfig, State]]
AsyncGetConfigForIssuer = Callable[[str], Awaitable[Tuple[ValidationConfig, State]]]


@overload
def validate_multi_tenant_response(
    *,
    data: Union[bytes, str],
    get_config_for_issuer: SyncGetConfigForIssuer[State],
    expected_audience: str,
) -> Tuple[Response, State]:
    pass


@overload
def validate_multi_tenant_response(
    *,
    data: Union[bytes, str],
    get_config_for_issuer: AsyncGetConfigForIssuer[State],
    expected_audience: str,
) -> Awaitable[Tuple[Response, State]]:
    pass


def validate_multi_tenant_response(
    *,
    data: Union[bytes, str],
    get_config_for_issuer: Union[
        SyncGetConfigForIssuer[State], AsyncGetConfigForIssuer[State]
    ],
    expected_audience: str,
) -> Union[Tuple[Response, State], Awaitable[Tuple[Response, State]]]:
    xml = base64.b64decode(data)
    tree = utils.deserialize_xml(xml)
    assertion = find_or_raise(tree, "./saml:Assertion")
    issuer = find_or_raise(assertion, "./saml:Issuer").text
    maybe_awaitable = get_config_for_issuer(issuer)

    if isinstance(maybe_awaitable, tuple):
        config, state = maybe_awaitable
        return (
            validate_response(
                data=data,
                certificate=config.certificate,
                expected_audience=expected_audience,
                idp_issuer=issuer,
                signature_verification_config=config.signature_verification_config,
                allowed_time_drift=config.allowed_time_drift,
            ),
            state,
        )
    else:
        result_future: "asyncio.Future[Tuple[Response, State]]" = asyncio.Future()

        def handle_result(
            task: "asyncio.Future[Tuple[ValidationConfig, State]]",
        ) -> None:
            if task.cancelled():
                result_future.cancel()
            exc = task.exception()
            if exc is not None:
                result_future.set_exception(exc)
                return
            config, state = task.result()
            try:
                result_future.set_result(
                    (
                        validate_response(
                            data=data,
                            certificate=config.certificate,
                            expected_audience=expected_audience,
                            idp_issuer=issuer,
                            signature_verification_config=config.signature_verification_config,
                            allowed_time_drift=config.allowed_time_drift,
                        ),
                        state,
                    )
                )
            except Exception as exc:
                result_future.set_exception(exc)

        task = asyncio.ensure_future(maybe_awaitable)
        task.add_done_callback(handle_result)
        return result_future


def validate_response(
    *,
    data: Union[bytes, str],
    certificate: Union[Certificate, Collection[Certificate]],
    expected_audience: str,
    idp_issuer: str,
    signature_verification_config: VerifyConfig = VerifyConfig.default(),
    allowed_time_drift: TimeDriftLimits = TimeDriftLimits.none(),
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
    if issuer != idp_issuer:
        raise IssuerMismatch(received_issuer=issuer, expected_issuer=idp_issuer)
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
    if now + allowed_time_drift.not_before_max_drift < not_before:
        raise ResponseTooEarly(observed_time=now, not_before=not_before)
    if now - allowed_time_drift.not_on_or_after_max_drift >= not_on_or_after:
        raise ResponseExpired(observed_time=now, not_on_or_after=not_on_or_after)

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
