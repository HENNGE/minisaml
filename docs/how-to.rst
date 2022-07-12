.. _how-to:

#############
How To Guides
#############


Prevent :term:`Identity Provider` Initiated SSO
===============================================

To prevent :term:`Identity Provider` Initiated SSO, you must pass a ``request_id`` to
:py:func:`minisaml.request.get_request_redirect_url` and store that ``request_id``. Then,
after validating the :term:`SAML Response` with :py:func:`minisaml.response.validate_response`,
confirm that the :py:attr:`minisaml.response.Response.in_response_to` contains a request ID generated
by you.



Allow non-SHA256-algorithms in :term:`SAML Responses<SAML Response>`
====================================================================

By default, MiniSAML expects :term:`SAML Responses<SAML Response>` to be signed using SHA-256.
To allow different algorithms, you have to provide the ``signature_verification_config`` argument when calling
:py:func:`minisaml.response.validate_response`. The argument should be an instance of :py:class:`minisignxml.config.VerifyConfig`, which
takes two arguments ``allowed_signature_method`` and ``allowed_digest_method`` both collections of types (not instances)
of hash algorithms from :py:mod:`cryptography.hazmat.primitives.hashes`.


Allow multiple certificates when validating a response
======================================================

In some cases, such as when an :term:`Identity Provider` changes their certificate, you might want
:py:func:`minisaml.response.validate_response` to accept multiple certificates. To do so, instead of passing
a single certificate object, pass it a collection of certificates. You may check the
:py:attr:`minisaml.response.Response.certificate` attribute on the :py:class:`minisaml.response.Response` object
returned by :py:func:`minisaml.response.validate_response` to check which certificate was actually used.


Allow for inaccurate clocks
===========================

:term:`SAML Responses<SAML Response>` include two timestamps limiting the validity period
of the response, ``NotBefore`` defines the lower bound and ``NotOnOrAfter`` defines the upper bound.
Since the clocks of different computers are not always in perfect sync, minisaml allows you to define
a maximum amount of inaccuracy for both of those values when validating responses. To do so,
provide an instance if :py:class:`minisaml.response.TimeDriftLimits` as the ``allowed_time_drift`` argument
to :py:func:`minisaml.response.validate_response`.

Supporting SAML in a multi-tenant system
========================================

If you want to have a single :term:`Assertion Consumer Service` used by multiple :term:`Identity Providers <Identity Provider>`,
you would not know which certificate to use to validate the response before parsing the response. To that end, MiniSAML provides
the :py:func:`minisaml.response.validate_multi_tenant_response` API, which validates the response in two steps. First, it will
extract the :term:`Issuer` of the :term:`Identity Provider`, then call the callback function ``get_config_for_issuer`` passed to
it with the :term:`Issuer` as its only argument. This callback may be synchronous or asynchronous, the return value of
:py:func:`minisaml.response.validate_multi_tenant_response` becoming asynchronous if the callback is asynchronous. The callback
should return a tuple of a :py:class:`minisaml.response.ValidationConfig` instance and a value to also be returned by
:py:func:`minisaml.response.validate_multi_tenant_response`, the second value making it possible to re-use calculations done
in the callback. If the :term:`Issuer` is not supported, the callback function should raise an exception.

Here's a fictional example on how to use this API::

    def request_handler(request):
        try:
            response, tenant_info = validate_multi_tenant_response(
                data=request.get_form_data("SAMLRequest"),
                get_config_for_issuer=get_config_for_issuer,
                expected_audience="https://my.sp/issuer"
            )
        except MiniSAMLError:
            # handle bad saml response
        except TenantNotFound:
            # handle unknown tenant
        # handle validated response

    def get_config_for_issuer(issuer: str) -> tuple[ValidationConfig, TenantInfo]:
        tenant_info = get_tenant_info_from_saml_issuer(issuer)
        if not tenant_info:
            raise TenantNotFound()
        return ValidationConfig(
            certificate=tenant_info.saml_certificate,
        ), tenant_info

    class TenantNotFound(Exception):
        pass
