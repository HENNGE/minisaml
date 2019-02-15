# MiniSAML


Absolutely minimalistic SAML 2 client. Does not support the full SAML 2 specification, on purpose.
Basically it only supports requests via HTTP Redirect and responses via HTTP POST.


## Usage


### Create a SAML Request

```python
from minisaml.request import get_request_redirect_url

url = get_request_redirect_url(
    saml_endpoint='https://your-idp.invalid/sso-endpoint/', 
    issuer='Your SAML Issuer', 
    acs_url='https://you.web-site.invalid/saml/acs/'
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
    response = validate_response(data=saml_response, certificate=certificate)
except:
    handle_invalid_response_somehow()

# response is a minisaml.response.Response object
```
