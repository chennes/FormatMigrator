# SPDX-License-Identifier: LGPL-2.1-or-later

from xml.etree.ElementTree import Element
from typing import List, Optional


def find_elements_by_type(root: Element, target_type: str) -> List[Element]:
    matches = []

    def recurse(node: Element):
        if node.attrib.get("type") == target_type:
            matches.append(node)
        for child in node:
            recurse(child)

    recurse(root)
    return matches


def find_first_element_with_name(root: Element, target_name: str) -> Optional[Element]:

    def recurse(node: Element) -> Optional[Element]:
        if node.attrib.get("Name") == target_name:
            return node
        for child in node:
            result = recurse(child)
            if result is not None:
                return result
        return None

    return recurse(root)