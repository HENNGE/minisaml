from minisignxml.internal.namespaces import make_namespace

from .constants import *

samlp = make_namespace("samlp", NAMES_SAML2_PROTOCOL)
saml = make_namespace("saml", NAMES_SAML2_ASSERTION)

NAMESPACE_MAP = {"samlp": NAMES_SAML2_PROTOCOL, "saml": NAMES_SAML2_ASSERTION}
