.. MiniSAML documentation master file, created by
   sphinx-quickstart on Fri Aug 14 11:50:57 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MiniSAML documentation!
==================================

MiniSAML is a Python library which allows building SAML 2 Service Providers easily.
It deliberately implements only a sub set of the SAML 2 specification, focusing on
the parts that are most likely to be encountered in the real world, in order to offer
a better API for developers and make it difficult to do the wrong thing.

:ref:`saml-intro`
=================

A short introduction to some basic SAML 2 concepts which are supported by MiniSAML.

:ref:`tutorial`
===============

A complete walk through on how to build accept SAML authentication in your application.


:ref:`how-to`
=============

Practical guides on some more advanced use cases.

:ref:`reference`
================

API references.

.. toctree::
    :maxdepth: 2
    :hidden:

    how-to
    reference
    saml-intro
    tutorial

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
