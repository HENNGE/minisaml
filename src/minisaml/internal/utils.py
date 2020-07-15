from lxml.etree import _Element as Element
from minisignxml.internal import utils

from .namespaces import NAMESPACE_MAP


def find_or_raise(element: Element, path: str) -> Element:
    return utils.find_or_raise(element, path, NAMESPACE_MAP)
