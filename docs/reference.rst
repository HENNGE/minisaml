.. _reference:

#############
API Reference
#############

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



``minisaml.response.validate_response``
=======================================

.. autofunction:: minisaml.response.validate_response

    :param data: :term:`SAML Response` as extracted from the HTTP form field ``SAMLResponse``.
    :param certificate: Certificate or collection of certificates used by the :term:`Identity Provider`.
    :param expected_audience str: :term:`Audience` of your :term:`Identity Provider`.
    :param signature_verification_config: If the :term:`Identity Provider` uses an algorithm other than SHA-256 for
        response signing, you have to enable it by passing an appropriate :py:class:`minisignxml.config.VerifyConfig` instance.
    :param allowed_time_drift: Limits the amount of clock inaccuracy tolerated. Defaults to no inaccuracy allowed.
    :returns: Validated response.
    :raises minisaml.errors.MalformedSAMLResponse:
    :raises minisaml.errors.ResponseExpired:
    :raises minisaml.errors.ResponseTooEarly:
    :raises minisaml.errors.AudienceMismatch:
    :raises lxml.LxmlError:


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