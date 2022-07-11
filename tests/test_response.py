import asyncio
import datetime
from typing import Any, List, Tuple

import pytest
from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import Certificate
from defusedxml.lxml import fromstring
from minisignxml.config import VerifyConfig
from minisignxml.errors import UnsupportedAlgorithm
from time_machine import TimeMachineFixture

from minisaml.errors import (
    AudienceMismatch,
    IssuerMismatch,
    ResponseExpired,
    ResponseTooEarly,
)
from minisaml.response import (
    Attribute,
    TimeDriftLimits,
    ValidationConfig,
    gather_attributes,
    validate_multi_tenant_response,
    validate_response,
)
from tests.conftest import Read


@pytest.mark.usefixtures("good_time")
def test_saml_response_ok(response_xml_b64: bytes, cert: Certificate) -> None:
    response = validate_response(
        data=response_xml_b64,
        certificate=cert,
        expected_audience="https://sp.invalid",
        idp_issuer="https://idp.invalid",
    )
    assert response.name_id == "user.name"
    assert response.audience == "https://sp.invalid"
    assert response.in_response_to == "8QmO2elg5T6-GPgr7dZI7v27M-wvMXc1k76B6jleNmM"
    assert response.issuer == "https://idp.invalid"
    assert response.attrs == {"attr name": "attr value"}
    assert response.attributes[0].extra_attributes == {"ExtraAttribute": "hoge"}


@pytest.mark.usefixtures("good_time")
def test_saml_response_ok_multi_cert(
    response_xml_b64: bytes, cert: Certificate, cert2: Certificate
) -> None:
    response = validate_response(
        data=response_xml_b64,
        certificate={cert, cert2},
        expected_audience="https://sp.invalid",
        idp_issuer="https://idp.invalid",
    )
    assert response.certificate == cert


@pytest.mark.usefixtures("too_early")
def test_saml_response_too_early(response_xml_b64: bytes, cert: Certificate) -> None:
    with pytest.raises(ResponseTooEarly):
        validate_response(
            data=response_xml_b64,
            certificate=cert,
            expected_audience="https://sp.invalid",
            idp_issuer="https://idp.invalid",
        )


@pytest.mark.usefixtures("too_early")
def test_saml_response_too_early_allowed_time_drift(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    validate_response(
        data=response_xml_b64,
        certificate=cert,
        expected_audience="https://sp.invalid",
        idp_issuer="https://idp.invalid",
        allowed_time_drift=TimeDriftLimits(
            not_before_max_drift=datetime.timedelta(seconds=2),
            not_on_or_after_max_drift=datetime.timedelta(),
        ),
    )


@pytest.mark.usefixtures("too_late")
def test_saml_response_expired(response_xml_b64: bytes, cert: Certificate) -> None:
    with pytest.raises(ResponseExpired):
        validate_response(
            data=response_xml_b64,
            certificate=cert,
            expected_audience="https://sp.invalid",
            idp_issuer="https://idp.invalid",
        )


@pytest.mark.usefixtures("too_late")
def test_saml_response_expired_allowed_time_drift(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    validate_response(
        data=response_xml_b64,
        certificate=cert,
        expected_audience="https://sp.invalid",
        idp_issuer="https://idp.invalid",
        allowed_time_drift=TimeDriftLimits(
            not_before_max_drift=datetime.timedelta(),
            not_on_or_after_max_drift=datetime.timedelta(minutes=2),
        ),
    )


@pytest.mark.usefixtures("good_time")
def test_saml_response_audience_mismatch(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    with pytest.raises(AudienceMismatch):
        validate_response(
            data=response_xml_b64,
            certificate=cert,
            expected_audience="https://other.sp.invalid",
            idp_issuer="https://idp.invalid",
        )


@pytest.mark.usefixtures("good_time")
def test_saml_response_issuer_mismatch(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    with pytest.raises(IssuerMismatch):
        validate_response(
            data=response_xml_b64,
            certificate=cert,
            expected_audience="https://sp.invalid",
            idp_issuer="https://other.idp.invalid",
        )


@pytest.mark.usefixtures("good_time")
def test_saml_response_algorithm_mismatch(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    with pytest.raises(UnsupportedAlgorithm):
        validate_response(
            data=response_xml_b64,
            certificate=cert,
            expected_audience="https://other.sp.invalid",
            idp_issuer="https://idp.invalid",
            signature_verification_config=VerifyConfig(
                allowed_digest_method={hashes.SHA1},
                allowed_signature_method={hashes.SHA1},
            ),
        )


@pytest.mark.usefixtures("good_time")
def test_multi_tenant_saml_response(response_xml_b64: bytes, cert: Certificate) -> None:
    state = object()
    response, received_state = validate_multi_tenant_response(
        data=response_xml_b64,
        get_config_for_issuer=lambda issuer: (
            ValidationConfig(certificate=cert),
            state,
        ),
        expected_audience="https://sp.invalid",
    )
    assert received_state is state
    assert response.name_id == "user.name"
    assert response.audience == "https://sp.invalid"
    assert response.in_response_to == "8QmO2elg5T6-GPgr7dZI7v27M-wvMXc1k76B6jleNmM"
    assert response.issuer == "https://idp.invalid"
    assert response.attrs == {"attr name": "attr value"}
    assert response.attributes[0].extra_attributes == {"ExtraAttribute": "hoge"}


@pytest.mark.usefixtures("good_time")
async def test_multi_tenant_saml_response_async(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    state = object()

    async def get_config_for_issuer(issuer: str) -> Tuple[ValidationConfig, Any]:
        assert issuer == "https://idp.invalid"
        return ValidationConfig(certificate=cert), state

    response, received_state = await validate_multi_tenant_response(
        data=response_xml_b64,
        get_config_for_issuer=get_config_for_issuer,
        expected_audience="https://sp.invalid",
    )
    assert received_state is state
    assert response.name_id == "user.name"
    assert response.audience == "https://sp.invalid"
    assert response.in_response_to == "8QmO2elg5T6-GPgr7dZI7v27M-wvMXc1k76B6jleNmM"
    assert response.issuer == "https://idp.invalid"
    assert response.attrs == {"attr name": "attr value"}
    assert response.attributes[0].extra_attributes == {"ExtraAttribute": "hoge"}


@pytest.mark.usefixtures("good_time")
def test_multi_tenant_saml_response_error(
    response_xml_b64: bytes, cert: Certificate
) -> None:
    class Error(Exception):
        pass

    def get_config_for_issuer(issuer: str) -> Tuple[ValidationConfig, Any]:
        raise Error()

    with pytest.raises(Error):
        validate_multi_tenant_response(
            data=response_xml_b64,
            get_config_for_issuer=get_config_for_issuer,
            expected_audience="https://sp.invalid",
        )


@pytest.mark.usefixtures("good_time")
async def test_multi_tenant_saml_response_async_cancelled(
    response_xml_b64: bytes, cert: Certificate, monkeypatch: MonkeyPatch
) -> None:
    async def get_config_for_issuer(issuer: str) -> Tuple[ValidationConfig, None]:
        assert issuer == "https://idp.invalid"
        return ValidationConfig(certificate=cert), None

    original = asyncio.ensure_future

    def ensure_future_then_cancel(thing: Any) -> Any:
        fut = original(thing)
        fut.cancel()
        return fut

    monkeypatch.setattr(
        "minisaml.response.asyncio.ensure_future", ensure_future_then_cancel
    )

    with pytest.raises(asyncio.CancelledError):
        await validate_multi_tenant_response(
            data=response_xml_b64,
            get_config_for_issuer=get_config_for_issuer,
            expected_audience="https://sp.invalid",
        )


@pytest.mark.usefixtures("null_extract")
def test_azure_ad_response_parsing(
    azure_ad_unsigned_b64: bytes, time_machine: TimeMachineFixture, cert: Certificate
) -> None:
    time_machine.move_to(
        datetime.datetime(
            year=2013,
            month=3,
            day=18,
            hour=8,
            minute=48,
            second=15,
            microsecond=127000,
        )
    )

    response = validate_response(
        data=azure_ad_unsigned_b64,
        certificate=cert,
        expected_audience="https://www.contoso.com",
        idp_issuer="https://login.microsoftonline.com/82869000-6ad1-48f0-8171-272ed18796e9/",
    )
    assert response.in_response_to == "id758d0ef385634593a77bdf7e632984b6"


@pytest.mark.usefixtures("null_extract")
def test_azure_ad_response_microsecond_outdated(
    azure_ad_unsigned_b64: bytes, time_machine: TimeMachineFixture, cert: Certificate
) -> None:
    time_machine.move_to(
        datetime.datetime(
            year=2013,
            month=3,
            day=18,
            hour=8,
            minute=48,
            second=15,
            microsecond=128000,
        )
    )

    with pytest.raises(ResponseExpired):
        validate_response(
            data=azure_ad_unsigned_b64,
            certificate=cert,
            expected_audience="https://www.contoso.com",
            idp_issuer="https://login.microsoftonline.com/82869000-6ad1-48f0-8171-272ed18796e9/",
        )


@pytest.mark.parametrize(
    "filename,attributes,values",
    [
        (
            "attrs/single.xml",
            [
                Attribute(
                    name="AttrName",
                    values=["AttrValue"],
                    format=None,
                    extra_attributes={},
                )
            ],
            ["AttrValue"],
        ),
        (
            "attrs/multi.xml",
            [
                Attribute(
                    name="AttrName1",
                    values=["AttrValue1"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="AttrName2",
                    values=["AttrValue2"],
                    format=None,
                    extra_attributes={},
                ),
            ],
            ["AttrValue1", "AttrValue2"],
        ),
        (
            "attrs/multi-value.xml",
            [
                Attribute(
                    name="AttrName",
                    values=["AttrValue1", "AttrValue2"],
                    format=None,
                    extra_attributes={},
                )
            ],
            ["AttrValue1"],
        ),
        (
            "attrs/no-value.xml",
            [Attribute(name="AttrName", values=[], format=None, extra_attributes={})],
            [None],
        ),
        (
            "attrs/format.xml",
            [
                Attribute(
                    name="AttrName",
                    values=[],
                    format="name-format",
                    extra_attributes={},
                )
            ],
            [None],
        ),
        (
            "attrs/format-extra-attrs.xml",
            [
                Attribute(
                    name="AttrName",
                    values=[],
                    format="name-format",
                    extra_attributes={"ExtraAttribute": "Extra Attribute Value"},
                )
            ],
            [None],
        ),
        (
            "attrs/aad1.xml",
            [
                Attribute(
                    name="http://schemas.microsoft.com/identity/claims/tenantid",
                    values=["78c90aec-8019-47bf-88cb-5e561d975248"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="http://schemas.microsoft.com/identity/claims/objectidentifier",
                    values=["5b1141c1-a3d9-41f0-a51e-a3a5feb8f504"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="http://schemas.microsoft.com/identity/claims/identityprovider",
                    values=[
                        "https://sts.windows.net/78c90aec-8019-47bf-88cb-5e561d975248/"
                    ],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="http://schemas.microsoft.com/claims/authnmethodsreferences",
                    values=[
                        "http://schemas.microsoft.com/ws/2008/06/identity/authenticationmethod/password",
                        "http://schemas.microsoft.com/claims/multipleauthn",
                    ],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="http://schemas.microsoft.com/ws/2008/06/identity/claims/wids",
                    values=["b79fbf4d-3ef9-4689-8143-76b194e85509"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="emailaddress",
                    values=["r.k.test@sunyocc.edu"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="givenname", values=["Bob"], format=None, extra_attributes={}
                ),
                Attribute(
                    name="surname",
                    values=["Kras test"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="uid", values=["r.k.test"], format=None, extra_attributes={}
                ),
                Attribute(
                    name="occid", values=["1234567"], format=None, extra_attributes={}
                ),
                Attribute(
                    name="upn",
                    values=["r.k.test@sunyocc.edu"],
                    format=None,
                    extra_attributes={},
                ),
                Attribute(
                    name="groups",
                    values=[
                        "ITDept-ALL",
                        "ITDept-InfrastructureOnly",
                        "drupal_editors",
                    ],
                    format=None,
                    extra_attributes={},
                ),
            ],
            [
                "78c90aec-8019-47bf-88cb-5e561d975248",
                "5b1141c1-a3d9-41f0-a51e-a3a5feb8f504",
                "https://sts.windows.net/78c90aec-8019-47bf-88cb-5e561d975248/",
                "http://schemas.microsoft.com/ws/2008/06/identity/authenticationmethod/password",
                "b79fbf4d-3ef9-4689-8143-76b194e85509",
                "r.k.test@sunyocc.edu",
                "Bob",
                "Kras test",
                "r.k.test",
                "1234567",
                "r.k.test@sunyocc.edu",
                "ITDept-ALL",
            ],
        ),
        (
            "attrs/aad2.xml",
            [
                Attribute(
                    name="cn",
                    values=["r.k.test"],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
                Attribute(
                    name="sn",
                    values=["Kras test"],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
                Attribute(
                    name="givenName",
                    values=["Bob"],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
                Attribute(
                    name="memberOf",
                    values=[
                        "CN=drupal_editors,OU=Security Groups,OU=OCCUsers,DC=sunyocc,DC=edu\n        ",
                        "CN=ITDept-InfrastructureOnly,OU=Security\n            Groups,OU=OCCUsers,DC=sunyocc,DC=edu\n        ",
                    ],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
                Attribute(
                    name="sAMAccountName",
                    values=["r.k.test"],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
                Attribute(
                    name="userPrincipalName",
                    values=["r.k.test@sunyocc.edu"],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
                Attribute(
                    name="mail",
                    values=["robert.kras@gmail.com"],
                    format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
                    extra_attributes={},
                ),
            ],
            [
                "r.k.test",
                "Kras test",
                "Bob",
                "CN=drupal_editors,OU=Security Groups,OU=OCCUsers,DC=sunyocc,DC=edu\n        ",
                "r.k.test",
                "r.k.test@sunyocc.edu",
                "robert.kras@gmail.com",
            ],
        ),
    ],
)
def test_attributes(
    filename: str, attributes: List[Attribute], values: List[str], read: Read
) -> None:
    xml = read(filename)
    tree = fromstring(xml)
    result = list(gather_attributes(tree))
    assert result == attributes
    assert [attribute.value for attribute in result] == values
