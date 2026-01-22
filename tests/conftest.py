import datetime
from collections.abc import Callable, Collection
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from cryptography.x509 import Certificate, load_pem_x509_certificate
from defusedxml.lxml import fromstring
from lxml.etree import _Element as Element
from minisignxml.config import VerifyConfig
from time_machine import TimeMachineFixture


@pytest.fixture
def good_time(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(
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


@pytest.fixture
def too_early(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(
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


@pytest.fixture
def null_extract(monkeypatch: MonkeyPatch) -> None:
    def null_extract(
        *,
        xml: bytes,
        certificates: Collection[Certificate],
        config: VerifyConfig = VerifyConfig.default(),
    ) -> tuple[Element, Certificate]:
        return fromstring(xml), next(iter(certificates))

    monkeypatch.setattr(
        "minisaml.response.extract_verified_element_and_certificate", null_extract
    )


@pytest.fixture
def too_late(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(
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


Read = Callable[[str], bytes]


@pytest.fixture(scope="session")
def read() -> Read:
    def reader(filename: str) -> bytes:
        with Path(__file__).parent.joinpath("data", filename).open("rb") as fobj:
            return fobj.read()

    return reader


@pytest.fixture(scope="session")
def response_xml_b64(read: Read) -> bytes:
    return read("response.xml.b64")


@pytest.fixture(scope="session")
def azure_ad_unsigned_b64(read: Read) -> bytes:
    return read("azure_ad_unsigned.xml.b64")


@pytest.fixture(scope="session")
def cert(read: Read) -> Certificate:
    return load_pem_x509_certificate(read("cert.pem"))


@pytest.fixture(scope="session")
def cert2(read: Read) -> Certificate:
    return load_pem_x509_certificate(read("cert2.pem"))
