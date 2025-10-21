# SPDX-License-Identifier: LGPL-2.1-or-later

from xml.etree.ElementTree import Element
from typing import List


def find_elements_by_type(root: Element, target_type: str) -> List[Element]:
    matches = []

    def recurse(node: Element):
        if node.attrib.get("type") == target_type:
            matches.append(node)
        for child in node:
            recurse(child)

    recurse(root)
    return matches
