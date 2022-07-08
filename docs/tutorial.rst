.. _tutorial:

########
Tutorial
########

Installing MiniSAML
===================

MiniSAML requires Python 3.7 or newer. You should be able to install MiniSAML using pip
or another compatible Python package installer, such as poetry or Pipenv.

MiniSAML depends on two libraries that require C-extensions, `lxml`_ and `cryptography`_.
If there are no binary wheels available for your platform for these dependencies and you
are running into problems installing them, please refer to their respective documentation
for install instructions.

MiniSAML works with any web framework, as long as it is able to redirect users to a URL and
can accept POST requests. MiniSAML does not perform any IO itself.

Configuration
=============

MiniSAML needs some information about the :term:`Identity Provider` and your own application to work:

* The absolute URL to the SAML endpoint of the :term:`Identity Provider`.
* The :term:`Issuer` of the :term:`Identity Provider`.
* The :term:`Audience` your :term:`Service Provider` uses.
* The SAML Certificate your :term:`Identity Provider` uses. MiniSAML only supports RSA based certificates.
* The algorithms used by the :term:`Identity Provider` to sign the :term:`SAML Response`.
  By default MiniSAML only allows SHA-256. If your :term:`Identity Provider` uses a different
  algorithm, you have to opt-in explicitly.
* The absolute URL to the :term:`Assertion Consumer Service` in your application.


Generating a :term:`SAML Request`
=================================

To generate a :term:`SAML Request`, call :py:func:`minisaml.request.get_request_redirect_url`. This function
will return a string containing an absolute URL. You should redirect your user to that URL with a temporary
HTTP redirect.

For a detailed description of the arguments that function takes, please refer to its API reference. The
most basic call requires three keyword arguments:

* ``saml_endpoint``: The absolute URL to the SAML endpoint of the :term:`Identity Provider`.
* ``expected_audience``: The :term:`Audience` your :term:`Service Provider` uses.
* ``acs_url``: The absolute URL to the :term:`Assertion Consumer Service` in your application.

For example, if the SAML endpoint of your :term:`Identity Provider` is ``https://idp.invalid/saml/endpoint/``, your
:term:`Audience` is ``https://sp.invalid/example/`` and the :term:`Assertion Consumer Service` is ``https://sp.invalid/acs/example/``,
the call would be::

    from minisaml.request import get_request_redirect_url

    url = get_request_redirect_url(
        saml_endpoint='https://your-idp.invalid/saml/endpoint/',
        expected_audience='https://sp.invalid/example/',
        acs_url='https://sp.invalid/acs/example/'
    )

Consuming a :term:`SAML Response`
=================================

The :term:`SAML Response` will be sent via a HTTP POST request, so ensure your handler accepts those and
disable `CSRF`_ protection for that handler.

When your handler is called, read the :term:`SAML Response` from the HTTP Request body. The HTTP Request contains
form encoded data and the :term:`SAML Response` is in a field named ``SAMLResponse``. Pass the value of that field,
unaltered, to MiniSAML to parse and verify the response.

Once you have your ``SAMLResponse``, call :py:func:`validate_response`.

For a detailed description of the arguments that function takes, please refer to its API reference. The
most basic call requires three keyword arguments:

* The :term:`SAML Response` from the form data.
* The :term:`Issuer` your :term:`Identity Provider` uses.
* The SAML Certificate your :term:`Identity Provider` uses.
* The :term:`Audience` your :term:`Service Provider` uses.

Continuing the example from above, and assuming you store the SAML Certificate at ``/path/idp-certificate.pem`` as a PEM
encoded file and you have the :term:`SAML Response` data in a variable called ``saml_response``, the call would be::

    from cryptography.hazmat.backends import default_backend
    from cryptography.x509 import load_pem_x509_certificate
    from minisaml.response import validate_response

    with open('/path/idp-certificate.pem', 'rb') as fobj:
        certificate = load_pem_x509_certificate(fobj.read(), default_backend())

    response = validate_response(
        data=saml_response,
        certificate=certificate,
        expected_audience='https://sp.invalid/example/',
        idp_issuer='https://idp.invalid/example',
    )

:py:func:`validate_response` will either return a :py:class:`minisaml.response.Response` if the :term:`SAML Response`
was valid, or otherwise raise an exception. See the API reference for what exceptions may be raised.

For detailed descriptions of the data available on a :py:class:`minisaml.response.Response` instance, refer to the API
documentation. The field you are likely most interested in is :py:attr:`minisaml.response.Response.name_id` which
contains the user identifier.


.. _lxml: https://pypi.org/project/lxml/
.. _cryptography: https://pypi.org/project/cryptography/
.. _CSRF: https://en.wikipedia.org/wiki/Cross-site_request_forgery
