.. _saml-intro:

##############################
A short introduction to SAML 2
##############################

For comprehensive information about SAML 2, please refer to the `specification`_. This guide will just
cover a sub section of SAML 2 which is covered by this library.


What is SAML
============

SAML, Security Assertion Markup Language, is a standard for authentication and authorization, commonly used
to provide single sign on capabilities to web applications. It is especially popular with companies as it
usually operates on an organization level, not a user level. With SAML, it is trivial to give every user in
your organization access to a service, as long as that service supports SAML.

Key concepts and terms
======================

.. glossary::

    Service Provider
        A service, often a web application, which can be logged into using SAML.
        If you're using MiniSAML, you're building a :term:`Service Provider`.
        :term:`Service Provider` is often shortened to SP.

    Identity Provider
        A web application which manages users and their authentication.
        An :term:`Identity Provider` receives :term:`SAML Requests<SAML Request>` and sends :term:`SAML Response<SAML Response>`
        to :term:`Service Providers<Service Provider>`.
        MiniSAML does not provide support for building Identity Providers.
        Identity Provider is often shortened to IdP.

    SAML Request
        A request sent from the :term:`Service Provider` to the :term:`Identity Provider` to
        authenticate a user. MiniSAML generates these for you.

    Relay State
        Extra information contained in a :term:`SAML Request` which is unrelated to SAML.
        This is sent back together with the :term:`SAML Response` in case of successful
        authentication. The main use-case is to remember the path in your web application
        the user attempted to access before authentication in order to redirect them there
        after successful authentication.
        MiniSAML supports including a :term:`Relay State` in your :term:`SAML Request`, but
        it is your responsibility to retrieve it when processing the :term:`SAML Response` and
        to ensure that the value is valid.

    SAML Response
        Sent from the :term:`Identity Provider` to the :term:`Service Provider` containing the
        result of the :term:`SAML Request`. MiniSAML parses these for you.

    Audience
        Identifier of a :term:`Service Provider`. This is used by the :term:`Identity Provider` to
        distinguish different :term:`Service Provider`.
        The specification also calls this the *Issuer* of a :term:`Service Provider`, but to prevent confusion with *Issuer* of the :term:`Identity Provider`, MiniSAML refers to this as :term:`Audience`.
        :term:`Audience` is called *Entity ID* by some :term:`Identity Providers<Identity Provider>`.

    Assertion Consumer Service
        An endpoint on the :term:`Service Provider` which handles :term:`SAML Response` sent from
        the :term:`Identity Provider`. Assertion Consumer Service is often shortened to ACS.



How does SAML work
==================

Before using SAML, the :term:`Service Provider` has to be registered with the :term:`Identity Provider`. How this
is done differs from :term:`Identity Provider` to :term:`Identity Provider` and therefore is out of scope for this
document.

1. A user attempts to access a :term:`Service Provider` and needs to be authenticated.
2. The :term:`Service Provider` redirects the user to the :term:`Identity Provider` with a :term:`SAML Request`.
3. The :term:`Identity Provider` parses the :term:`SAML Request`, verifies the :term:`Service Provider` using the
   :term:`Audience` specified in the :term:`SAML Request`, then authenticates the user, for example by asking them
   for a username and password.
4. If the authentication on the :term:`Identity Provider` is successful, the :term:`Identity Provider` redirects
   the user back to the :term:`Service Provider` by sending a HTTP POST request to the :term:`Assertion Consumer Service`
   of the :term:`Service Provider`
5. The :term:`Service Provider` parses the :term:`SAML Response` and ensures that it is from the :term:`Identity Provider`.

.. mermaid::

    sequenceDiagram
        participant SP as Service Provider
        participant IdP as Identity Provider
        participant U as User

        U->>SP: Access web app
        SP->>IdP: SAML Request
        IdP->>U: Authenticate
        IdP->>SP: SAML Response

Some :term:`Service Provider` also support what is called *Identity Provider Initiated SSO*, in which case the user
directly access the :term:`Service Provider` from the :term:`Identity Provider` and there is no :term:`SAML Request`
involved, only a :term:`SAML Response`.


.. _specification: http://saml.xml.org/saml-specifications
