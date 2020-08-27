import datetime
from pathlib import Path

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import load_pem_x509_certificate
from defusedxml.lxml import fromstring
from minisignxml.config import VerifyConfig
from minisignxml.errors import UnsupportedAlgorithm

from minisaml.errors import AudienceMismatch, ResponseExpired, ResponseTooEarly
from minisaml.response import validate_response


@pytest.fixture
def read():
    def reader(filename: str) -> bytes:
        with Path(__file__).parent.joinpath(filename).open("rb") as fobj:
            return fobj.read()

    return reader


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
        return tree

    monkeypatch.setattr("minisaml.response.extract_verified_element", null_extract)
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
        return tree

    monkeypatch.setattr("minisaml.response.extract_verified_element", null_extract)
    with pytest.raises(ResponseExpired):
        validate_response(
            data=xml, certificate=None, expected_audience="https://www.contoso.com"
        )
