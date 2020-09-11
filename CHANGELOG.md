# Changelog

## next (unreleased)

* **Breaking** `minisaml.repsonse.Attribute.value` is now of type `Optional[str]`
* **Breaking** `minisaml.response.Response.attrs` is now of type `Dict[str, Optional[str]]`
* Improved support for Attribute Statements. Attributes with multiple values or no values are now supported.
* Added `minisaml.response.Attribute.values` (`List[str]`)

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
