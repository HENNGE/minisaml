# Changelog

## 23.1

* Added support for `saml_endpoint` URLs with a query string in `minisaml.request.get_request_redirect_url` thanks to a
  contribution by [@thesebas](https://github.com/thesebas).

## 22.7

* **Breaking** `minisaml.response.validate_response` now requires an additional parameter `idp_issuer`.
* **Breaking** Several dependencies had their minimum supported version updated.
* Added `minisaml.response.validate_multi_tenant_response` to make integrating MiniSAML into multi-tenant systems easier
  and safer.

## 22.6

* Added `allowed_time_drift` parameter to `minisaml.response.validate_response` to allow for clock inaccuracies when validating SAML responses.
* `minisaml.errors.ResponseExpired` now stores both the observed time and the time limit of the SAML response as attributes on the exception.
* `minisaml.errors.ResponseTooEarly` now stores both the observed time and the time limit of the SAML response as attributes on the exception.
* Added more documentation, changed documentation theme.

## 22.4

* Minimum supported minisignxml version is now 22.4.

## 20.11b0

* Allow passing multiple certificates to `minisaml.repsonse.validate_response` to allow certificate rollover.
* Added the certificate used in `minisaml.repsonse.validate_response` to the returned `minisaml.repsonse.Response`.
* Minimum supported minisignxml version is now 20.11b0.

## 20.9b1

* **Breaking** `minisaml.repsonse.Attribute.value` is now of type `Optional[str]`
* **Breaking** `minisaml.response.Response.attrs` is now of type `Dict[str, Optional[str]]`
* Improved support for Attribute Statements. Attributes with multiple values or no values are now supported.
* Added `minisaml.response.Attribute.values` (`List[str]`)
* Fixed incorrect Base64 encoding of SAML Requests.

## 20.8b3

* Support sub-second resolution for datetimes in SAML responses.

## 20.8b2

* Fix minisignxml dependency specifier

## 20.8b1

* Support SAML signatures with non-SHA256 digest and signinig algorithms
* Relaxed type hint for validate_response to allow strings as well as bytes.
* Added documentation.

## 20.8b0

* NameFormat on saml:Attribute is optional

## 20.7b0

* Initial release
