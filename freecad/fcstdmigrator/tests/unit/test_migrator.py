# SPDX-License-Identifier: LGPL-2.1-or-later

import unittest
from datetime import date
from xml.etree.ElementTree import Element
from packaging.version import Version

from freecad.fcstdmigrator.migrator import Migrator


class TestMigratorMeta(unittest.TestCase):

    def test_cannot_instantiate_migrator_directly(self):
        with self.assertRaises(TypeError):
            Migrator()

    def test_missing_required_attribute_raises(self):
        with self.assertRaises(TypeError):

            class BadMigrator(Migrator):
                name = "Bad"
                description = "Missing one attribute"
                changed_in_freecad_version = Version("0.1")
                changed_on_date = date.today()
                # Oops, forgot changed_in_hash

                def forward(self, d, g): ...
                def backward(self, d, g): ...

    def test_incorrect_attribute_type_raises(self):
        with self.assertRaises(TypeError):

            class WrongTypeMigrator(Migrator):
                name = "Wrong"
                description = "Wrong type for one field"
                changed_in_freecad_version = Version("1.0")
                changed_on_date = date.today()
                changed_in_hash = 12345  # not a str

                def forward(self, d, g): ...
                def backward(self, d, g): ...

    def test_valid_subclass_is_accepted(self):
        class GoodMigrator(Migrator):
            name = "Good"
            description = "All attributes present and valid"
            changed_in_freecad_version = Version("1.0")
            changed_on_date = date.today()
            changed_in_hash = "abc123"

            def forward(self, d, g): ...
            def backward(self, d, g): ...

        instance = GoodMigrator()
        self.assertIsInstance(instance, Migrator)
        self.assertEqual(GoodMigrator.name, "Good")
        self.assertIsInstance(GoodMigrator.changed_in_freecad_version, Version)

    def test_subclass_must_implement_abstract_methods(self):

        class IncompleteMigrator(Migrator):
            name = "Incomplete"
            description = "Missing backward"
            changed_in_freecad_version = Version("1.0")
            changed_on_date = date.today()
            changed_in_hash = "hash"

            def forward(self, d, g): ...

            # Hey, where is backward?

        with self.assertRaises(TypeError):
            # We have to actually instantiate the class to trigger the error.
            IncompleteMigrator()


class TestMigratorStaticMethods(unittest.TestCase):
    def test_rename_property(self):
        root = Element("Root")
        prop = Element("Property", name="OldName")
        root.append(prop)
        Migrator.rename_property(root, "OldName", "NewName")
        self.assertEqual(prop.get("name"), "NewName")

    def test_change_property_type(self):
        root = Element("Root")
        prop = Element("Property", name="prop1", type="oldtype")
        root.append(prop)

        def add_value(elem):
            elem.set("value", "42")

        Migrator.change_property_type(root, "prop1", "newtype", transformation=add_value)
        self.assertEqual(prop.get("type"), "newtype")
        self.assertEqual(prop.get("value"), "42")

    def test_transform_property(self):
        root = Element("Root")
        prop = Element("Property", name="target")
        root.append(prop)

        def mark(elem):
            elem.set("transformed", "yes")

        Migrator.transform_property(root, "target", mark)
        self.assertEqual(prop.get("transformed"), "yes")
