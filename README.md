# MiniSAML


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CircleCI](https://circleci.com/gh/HENNGE/minisaml.svg?style=svg)](https://circleci.com/gh/HENNGE/minisaml)
[![Documentation Status](https://readthedocs.org/projects/minisaml/badge/?version=latest)](https://minisaml.readthedocs.io/en/latest/?badge=latest)



Absolutely minimalistic SAML 2 client. Does not support the full SAML 2 specification, on purpose.
It only supports requests via HTTP Redirect and responses via HTTP POST.


## Usage


### Create a SAML Request

```python
from minisaml.request import get_request_redirect_url

url = get_request_redirect_url(
    saml_endpoint="https://your-idp.invalid/sso-endpoint/",
    expected_audience="Your SAML Issuer",
    acs_url="https://you.web-site.invalid/saml/acs/"
)

# This line depends on your web framework/server
redirect_user_to_url(url)
```

### Validate and parse the SAML Response

```python
from minisaml.response import validate_response

# This line depends on your web framework/server
saml_response = get_SAMLResponse_form_data_as_bytes()

# Load the x509 certificate as a cryptography.x509.Certificate somehow
certificate = ...

try:
    response = validate_response(
        data=saml_response,
        certificate=certificate,
        expected_audience="Your SAML Issuer",
        idp_issuer="https://your-idp.invalid/issuer/"
    )
except:
    handle_invalid_response_somehow()

# response is a minisaml.response.Response object
```
