# SPDX-License-Identifier: LGPL-2.1-or-later

from unittest import TestCase
from xml.etree.ElementTree import Element

from freecad.fcstdmigrator.xml_utilities import find_elements_by_type, find_first_element_with_name


class TestFindElementsByType(TestCase):

    def test_finds_matching_elements(self):
        root = Element("root")
        child1 = Element("child", type="A")
        child2 = Element("child", type="B")
        child3 = Element("child", type="A")
        root.extend([child1, child2, child3])

        result = find_elements_by_type(root, "A")
        self.assertEqual(set(r.attrib["type"] for r in result), {"A"})
        self.assertEqual(len(result), 2)
        self.assertIn(child1, result)
        self.assertIn(child3, result)
        self.assertNotIn(child2, result)

    def test_finds_nested_matches(self):
        root = Element("root")
        inner = Element("inner", type="target")
        middle = Element("middle")
        middle.append(inner)
        root.append(middle)

        result = find_elements_by_type(root, "target")
        self.assertEqual(result, [inner])

    def test_returns_empty_when_no_match(self):
        root = Element("root")
        root.append(Element("child", type="other"))
        result = find_elements_by_type(root, "missing")
        self.assertEqual(result, [])

    def test_includes_root_if_it_matches(self):
        root = Element("root", type="root-type")
        result = find_elements_by_type(root, "root-type")
        self.assertEqual(result, [root])

    def test_handles_mixed_structure(self):
        root = Element("root")
        a1 = Element("a", type="T")
        a2 = Element("a")
        b1 = Element("b", type="T")
        a2.append(b1)
        root.extend([a1, a2])

        result = find_elements_by_type(root, "T")
        self.assertEqual(set(result), {a1, b1})
        self.assertTrue(all(isinstance(e, Element) for e in result))


class TestFindFirstElementWithName(TestCase):

    def test_finds_first_matching_child(self):
        root = Element("root")
        a = Element("a", attrib={"Name":"x"})
        b = Element("b", attrib={"Name":"target"})
        root.extend([a, b])

        result = find_first_element_with_name(root, "target")
        self.assertIs(result, b)

    def test_finds_nested_match(self):
        root = Element("root")
        a = Element("a")
        inner = Element("inner", attrib={"Name":"target"})
        a.append(inner)
        root.append(a)

        result = find_first_element_with_name(root, "target")
        self.assertIs(result, inner)

    def test_returns_first_match_in_depth_first_order(self):
        root = Element("root")

        # Branch 1 (contains target early)
        a = Element("a")
        a1 = Element("a1", attrib={"Name":"target"})
        a.append(a1)

        # Branch 2 (also contains target but later)
        b = Element("b")
        b1 = Element("b1", attrib={"Name":"target"})
        b.append(b1)

        root.extend([a, b])

        result = find_first_element_with_name(root, "target")
        self.assertIs(result, a1)

    def test_returns_none_when_no_match(self):
        root = Element("root")
        root.append(Element("child", attrib={"Name":"foo"}))
        result = find_first_element_with_name(root, "bar")
        self.assertIsNone(result)
