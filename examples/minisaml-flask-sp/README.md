A simple flask app which authenticates users via a SAML IdP. Only supports a single tenant. Allows IdP initiated login.

To run, set the following environment variables:

* `MINISAML_CERT_PEM_PATH` path to the Identity Providers SAML signing certificate in PEM format.
* `MINISAML_ENDPOINT` the Identity Providers SAML endpoint.
* `MINISAML_ISSUER` the SAML Issuer to use.
