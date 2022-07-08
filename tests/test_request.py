import datetime

import pytest
from time_machine import TimeMachineFixture

from minisaml.request import get_request_redirect_url


def test_base64_encoding(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(
        datetime.datetime(
            year=2020,
            month=9,
            day=14,
            hour=14,
            minute=20,
            second=11,
            tzinfo=datetime.timezone.utc,
        )
    )
    url = get_request_redirect_url(
        saml_endpoint="https://saml.invalid",
        expected_audience="audience",
        acs_url="https://acs.invalid",
        request_id="テスト",
        force_reauthentication=False,
    )
    assert (
        url
        == "https://saml.invalid/?SAMLRequest=fZHPSsNAEMZfJew9f%2BnFoSlUixioGtroobd1M7ULyWzc2S16tSC%2Bks/TFzGmKgWxx5n55jffx4xZtk0HU%2B82tMAnj%2ByC57YhhmGQC28JjGTNQLJFBqdgOb2eQxYl0FnjjDKNCKbMaJ02dGGIfYt2iXarFd4t5rnYONcxxLFUHGnaykbXIihmudjv3vavH/vde18yeyyInSSXiyzJkjA5C9NRlY4gSyBNVyIov8%2Bda6o1PZ729nAQMVxVVRmWt8tKBPdouffY86NETMZfCWE4bI8yn8bKn6BiIn2tkRSO4yPQgdrBTb9ZzErTaPUSXBrbSvc/OI3SoaPrcD1IwRN3qPRaY90bjf8yf5vHn5t8Ag%3D%3D"
    )
