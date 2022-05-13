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