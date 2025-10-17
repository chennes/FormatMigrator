# SPDX-License-Identifier: LGPL-2.1-or-later

from abc import ABC, ABCMeta, abstractmethod
from typing import Callable
from xml.etree.ElementTree import Element
from packaging.version import Version
from datetime import date


class MigratorException(Exception):
    """Base class for all exceptions raised by migrators."""


class IncompatibleVersionException(MigratorException):
    """Raised when a requested migration cannot be applied to the given FCStd file, for example,
    when a new feature is used in the current version and cannot be used in the older version.
    Should never be raised by forward-migration code."""


class MigratorMeta(ABCMeta):
    required_attrs = {
        "name": str,
        "description": str,
        "changed_in_freecad_version": Version,
        "changed_on_date": date,
        "changed_in_hash": str,
    }

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if cls.__name__ == "Migrator":
            return

        for attr, expected_type in MigratorMeta.required_attrs.items():
            if not hasattr(cls, attr):
                raise TypeError(f"Class '{name}' is missing required attribute '{attr}'")
            value = getattr(cls, attr)
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Attribute '{attr}' in class '{name}' must be of type {expected_type.__name__}, got {type(value).__name__}"
                )


class Migrator(ABC, metaclass=MigratorMeta):

    name: str = "Migrator Base Class"
    description: str = "Do not use this class directly."
    changed_in_freecad_version: Version = Version("0.0")
    changed_on_date: date = date.today()
    changed_in_hash: str = ""

    @abstractmethod
    def forward(self, document_xml: Element, gui_document_xml: Element):
        """Run a forward migration (e.g., upgrade from a previous version to a newer version)"""

    @abstractmethod
    def backward(self, document_xml: Element, gui_document_xml: Element):
        """Run a backward migration (e.g., downgrade from a newer version to a previous version).
        May raise an IncompatibleVersionException if the backward migration cannot be applied."""

    @staticmethod
    def rename_property(root: Element, old_name: str, new_name: str):
        """Rename a property."""
        for prop in root.iter("Property"):
            if prop.get("name") == old_name:
                prop.set("name", new_name)

    @staticmethod
    def change_property_type(
        root: Element, name: str, new_type: str, transformation: Callable = None
    ):
        for prop in root.iter("Property"):
            if prop.get("name") == name:
                prop.set("type", new_type)
                if transformation:
                    transformation(prop)

    @staticmethod
    def transform_property(root: Element, name: str, transformation: Callable):
        for prop in root.iter("Property"):
            if prop.get("name") == name:
                transformation(prop)
