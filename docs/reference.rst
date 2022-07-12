.. _reference:

#############
API Reference
#############

Request
*******

``minisaml.request.get_request_redirect_url``
=============================================

.. autofunction:: minisaml.request.get_request_redirect_url

    :param saml_endpoint: Absolute URL to the SAML endpoint of the :term:`Identity Provider`.
    :param expected_audience: :term:`Audience` of your :term:`Identity Provider`.
    :param acs_url: Absolute URL to the :term:`Assertion Consumer Service` handler of your application.
    :param force_reauthentication: Request re-authentication of the user, even if the user is already authenticated on the :term:`Identity Provider`. Not all :term:`Identity Providers<Identity Provider>` support this option.
    :param request_id: To prevent :term:`Identity Provider` initiated SSO, you can specify a unique request ID. It is your own responsibility to verify this when validating :term:`SAML Responses<SAML Response>`. If you don't provide a request ID, a random value will be used.
    :param relay_state: Any :term:`Relay State` you want to include in the :term:`SAML Request`.
    :return: Absolute URL to which the user should be redirected to using a temporary HTTP redirect.


Response
********

``minisaml.response.validate_response``
=======================================

.. autofunction:: minisaml.response.validate_response

    Use this to validate a response if you know the issuer. This should be the case if your
    app only supports a single tenant or if each tenant has a separate :term:`Assertion Consumer Service`
    endpoint. For multi-tenant apps using a single :term:`Assertion Consumer Service`, use
    :py:func:`minisaml.response.validate_multi_tenant_response` instead.

    :param data: :term:`SAML Response` as extracted from the HTTP form field ``SAMLResponse``.
    :param certificate: Certificate or collection of certificates used by the :term:`Identity Provider`.
    :param expected_audience: :term:`Issuer` of your :term:`Service Provider`.
    :param idp_issuer: The :term:`Issuer` of the :term:`Identity Provider` which issued the response.
    :param signature_verification_config: If the :term:`Identity Provider` uses an algorithm other than SHA-256 for
        response signing, you have to enable it by passing an appropriate :py:class:`minisignxml.config.VerifyConfig` instance.
    :param allowed_time_drift: Limits the amount of clock inaccuracy tolerated. Defaults to no inaccuracy allowed.
    :returns: Validated response.
    :raises minisaml.errors.MalformedSAMLResponse:
    :raises minisaml.errors.ResponseExpired:
    :raises minisaml.errors.ResponseTooEarly:
    :raises minisaml.errors.AudienceMismatch:
    :raises minisaml.errors.IssuerMismatch:
    :raises lxml.etree.LxmlError:

.. autofunction:: minisaml.response.validate_multi_tenant_response

    This function allows for easy support of multi-tenant systems, where a single :term:`Assertion Consumer Service`
    is used for multiple :term:`Identity Providers<Identity Provider>` and the configuration to validate the response
    depends on the :term:`Issuer` of the :term:`Identity Provider`.

    MiniSAML will parse the response and call the function passed to ``get_config_for_issuer`` with the :term:`Issuer`
    as the only argument. This function should then return a tuple of a :py:class:`minisaml.response.ValidationConfig`
    instance to use to validate the response and a second value which will be returned by :py:func:`minisaml.response.validate_multi_tenant_response`.
    This second value can be used to re-use values calculated in ``get_config_for_issuer``, if no such values are needed,
    use ``None`` as the second item in the tuple instead.
    Any exceptions raised in the ``get_config_for_issuer`` function will be forwarded
    to the caller of :py:func:`minisaml.response.validate_multi_tenant_response`, as such, exceptions should be used to
    signal an unsupported :term:`Issuer`.

    The other arguments to this function and the attributes on :py:class:`minisaml.response.ValidationConfig` have the
    same semantics as the arguments to :py:func:`minisaml.response.validate_response`.

    .. note::

        The ``get_config_for_issuer`` argument can be either a synchronous or an asynchronous function.
        If it is asynchronous, the return value of this function will also be asynchronous.

    :returns: Validated response or an awaitable future of the validated response.
    :raises minisaml.errors.MalformedSAMLResponse:
    :raises minisaml.errors.ResponseExpired:
    :raises minisaml.errors.ResponseTooEarly:
    :raises minisaml.errors.AudienceMismatch:
    :raises minisaml.errors.IssuerMismatch:
    :raises lxml.etree.LxmlError:

Data Types
**********


``minisaml.response.ValidationConfig``
======================================

.. autoclass:: minisaml.response.ValidationConfig
    :undoc-members:
    :members: certificate,signature_verification_config,allowed_time_drift


``minisaml.response.Response``
==============================

.. py:class:: minisaml.response.Response

    .. py:attribute:: issuer
        :type: str

        Issuer of the :term:`Identity Provider`

    .. py:attribute:: name_id
        :type: str

        User identifier. The value and format of this depend on the :term:`Identity Provider`.

    .. py:attribute:: audience
        :type: str

        :term:`Audience` of the :term:`Service Provider`.

    ..  py:attribute:: attributes
        :type: List[Attribute]

        Extra attributes in the :term:`SAML Response`.

    .. py:attribute:: session_not_on_or_after
        :type: Optional[datetime.datetime]

        A :term:`Identity Provider` may suggest a time after which the session created by this :term:`SAML Response` should be invalidated.

    .. py:attribute:: in_response_to
        :type: Optional[str]

        If the :term:`SAML Response` was generated in response to a :term:`SAML Request`, this will contain the request ID of that request. It is your responsibility to verify this value if you want to prevent :term:`Identity Provider` Initiated SSO.

    .. py:attribute:: attrs
        :type: Dict[str, str]

        The attributes from :py:attr:`minisaml.response.Response.attributes` as a dictionary.
        If the attributes contain multiple attributes with the same name, this dictionary will only
        hold one of them, use :py:attr:`minisaml.response.Response.attributes` instead.

    .. py:attribute:: certificate
        :type: cryptography.x509.Certificate

        The certificate used to sign this response.


``minisaml.response.Attribute``
===============================


.. py:class:: minisaml.response.Attribute

    .. py:attribute:: name
        :type: str

        Name of the attribute

    .. py:attribute:: value
        :type: Optional[str]

        Value of the attribute, if it has one. If the attribute has multiple values, the first one
        is returned. See :py:attr:`minisaml.response.Attribute.values` to get all values.

    .. py:attribute:: values
        :type: List[str]

        All values for this attribute, if any are given.

    .. py:attribute:: format
        :type: Optional[str]

        Format of the value if specified.

    .. py:attribute:: extra_attributes
        :type: Dict[str, str]

        Extra XML attributes on the attribute element.


``minisaml.response.TimeDriftLimits``
=====================================

.. py:class:: minisaml.response.TimeDriftLimits

    .. py:attribute:: not_before_max_drift
        :type: datetime.timedelta

    .. py:attribute:: not_on_or_after_max_drift
        :type: datetime.timedelta

    .. py:method:: none()
        :classmethod:

        Returns an instance which allows for no drift.

Exceptions
**********

``minisaml.errors.MiniSAMLError``
=================================

.. py:exception:: minisaml.errors.MiniSAMLError

    The base class for all errors raised by MiniSAML. Note that if you pass
    objects of the wrong types to MiniSAML APIs, normal Python exceptions such
    as ``TypeError`` may be raised as well. If the XML you pass to a response
    validation function is invalid, ``lxml`` may also raise an error.

``minisaml.errors.MalformedSAMLResponse``
=========================================

.. py:exception:: minisaml.errors.MalformedSAMLResponse

    The response was valid XML but not a valid SAML Response. Specifically, the
    signed element was neither a SAML Assertion nor a SAML Response.

``minisaml.errors.ResponseExpired``
===================================

.. py:exception:: minisaml.errors.ResponseExpired

    The response being validated is expired, beyond the time drift allowed by
    :py:class:`minisaml.response.TimeDriftLimits`.

    .. py:attribute:: observed_time
        :type: datetime.datetime

    .. py:attribute:: not_on_or_after
        :type: datetime.datetime

``minisaml.errors.ResponseTooEarly``
====================================

.. py:exception:: minisaml.errors.ResponseTooEarly

    The response being validated is too early, beyond the time drift allowed by
    :py:class:`minisaml.response.TimeDriftLimits`.

    .. py:attribute:: observed_time
        :type: datetime.datetime

    .. py:attribute:: not_before
        :type: datetime.datetime

``minisaml.errors.AudienceMismatch``
====================================

.. py:exception:: minisaml.errors.AudienceMismatch

    The audience in the SAML Response does not match the expected one passed to
    the validation function.

    .. py:attribute:: received_audience
        :type: str

    .. py:attribute:: expected_audience
        :type: str

``minisaml.errors.IssuerMismatch``
==================================


.. py:exception:: minisaml.errors.IssuerMismatch

    The issuer of the SAML Response does not match the expected one passed to
    the validation function.


    .. py:attribute:: received_issuer
        :type: str

    .. py:attribute:: expected_issuer
        :type: str
