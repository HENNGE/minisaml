import base64
import secrets
import zlib
from typing import Optional

from yarl import URL

from .internal.saml import build_saml_request


def get_request_redirect_url(
    *,
    saml_endpoint: str,
    expected_audience: str,
    acs_url: str,
    force_reauthentication: bool = False,
    request_id: Optional[str] = None,
    relay_state: Optional[str] = None,
) -> str:
    request_xml = build_saml_request(
        issuer=expected_audience,
        acs_url=acs_url,
        request_id=request_id or secrets.token_urlsafe(),
        force_reauthentication=force_reauthentication,
    )

    query = {
        "SAMLRequest": base64.urlsafe_b64encode(
            zlib.compress(request_xml)[2:-4]
        ).decode("utf-8")
    }
    if relay_state is not None:
        query["RelayState"] = relay_state
    return str(URL(saml_endpoint).with_query(query))
