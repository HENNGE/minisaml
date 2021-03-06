import datetime

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import load_pem_x509_certificate
from defusedxml.lxml import fromstring
from minisignxml.config import VerifyConfig
from minisignxml.errors import UnsupportedAlgorithm

from minisaml.errors import AudienceMismatch, ResponseExpired, ResponseTooEarly
from minisaml.response import Attribute, gather_attributes, validate_response


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_ok(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    response = validate_response(
        data=data, certificate=certificate, expected_audience="https://sp.invalid"
    )
    assert response.name_id == "user.name"
    assert response.audience == "https://sp.invalid"
    assert response.in_response_to == "8QmO2elg5T6-GPgr7dZI7v27M-wvMXc1k76B6jleNmM"
    assert response.issuer == "https://idp.invalid"
    assert response.attrs == {"attr name": "attr value"}
    assert response.attributes[0].extra_attributes == {"ExtraAttribute": "hoge"}


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_ok_multi_cert(read):
    data = read("response.xml.b64")
    expected_cert = load_pem_x509_certificate(read("cert.pem"), default_backend())
    other_cert = load_pem_x509_certificate(read("cert2.pem"), default_backend())
    response = validate_response(
        data=data,
        certificate={expected_cert, other_cert},
        expected_audience="https://sp.invalid",
    )
    assert response.certificate == expected_cert


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=30,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_too_early(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    with pytest.raises(ResponseTooEarly):
        validate_response(
            data=data,
            certificate=certificate,
            expected_audience="https://sp.invalid.com",
        )


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=34,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_expired(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    with pytest.raises(ResponseExpired):
        validate_response(
            data=data, certificate=certificate, expected_audience="https://sp.invalid"
        )


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_audience_mismatch(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    with pytest.raises(AudienceMismatch):
        validate_response(
            data=data,
            certificate=certificate,
            expected_audience="https://other.sp.invalid",
        )


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_algorithm_mismatch(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    with pytest.raises(UnsupportedAlgorithm):
        validate_response(
            data=data,
            certificate=certificate,
            expected_audience="https://other.sp.invalid",
            signature_verification_config=VerifyConfig(
                allowed_digest_method={hashes.SHA1},
                allowed_signature_method={hashes.SHA1},
            ),
        )


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2013, month=3, day=18, hour=8, minute=48, second=15, microsecond=127000
    )
)
def test_azure_ad_response_parsing(read, monkeypatch):
    xml = read("azure_ad_unsigned.xml")
    tree = fromstring(xml)

    def null_extract(**kwargs):
        return tree, None

    monkeypatch.setattr(
        "minisaml.response.extract_verified_element_and_certificate", null_extract
    )
    response = validate_response(
        data=xml, certificate=None, expected_audience="https://www.contoso.com"
    )
    assert response.in_response_to == "id758d0ef385634593a77bdf7e632984b6"


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2013, month=3, day=18, hour=8, minute=48, second=15, microsecond=128000
    )
)
def test_azure_ad_response_microsecond_outdated(read, monkeypatch):
    xml = read("azure_ad_unsigned.xml")
    tree = fromstring(xml)

    def null_extract(**kwargs):
        return tree, None

    monkeypatch.setattr(
        "minisaml.response.extract_verified_element_and_certificate", null_extract
    )
    with pytest.raises(ResponseExpired):
        validate_response(
            data=xml, certificate=None, expected_audience="https://www.contoso.com"
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
def test_attributes(filename, attributes, values, read):
    xml = read(filename)
    tree = fromstring(xml)
    result = list(gather_attributes(tree))
    assert result == attributes
    assert [attribute.value for attribute in result] == values
