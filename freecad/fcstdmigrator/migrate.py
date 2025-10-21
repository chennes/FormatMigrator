# SPDX-License-Identifier: LGPL-2.1-or-later

from packaging.version import Version, InvalidVersion
import zipfile
from defusedxml.ElementTree import parse
from xml.etree.ElementTree import Element, tostring
import re

from .discover import find_migrator_subclasses


class Migrate:
    """Primary migration class: instantiate with a FreeCAD file and a target version to perform
    an in-memory migration. Use the export() method to write the resulting FCStd file to disk."""

    def __init__(self, freecad_file: str, target_version: Version):
        self.freecad_file = freecad_file
        self.target_version = target_version
        self.original_version = target_version  # Overwritten with contents of Document.xml below
        self.document_xml = self.load_xml("Document.xml")
        self.gui_document_xml = self.load_xml("GuiDocument.xml")

        discovered_migrators = find_migrator_subclasses("migrations")
        self.migrators = sorted(discovered_migrators, key=lambda cls: cls.date)

        if self.target_version < self.original_version:
            self.run_backward_migration()
        elif self.target_version > self.original_version:
            self.run_forward_migration()
        else:
            print("No migration required, target version is the same as original version.")

    def load_xml(self, xml_file_name: str) -> Element:
        """Load an XML document from within the FCStd file (typically Document.xml or
        GuiDocument.xml)."""
        with zipfile.ZipFile(self.freecad_file, "r") as z:
            if xml_file_name not in z.namelist():
                raise FileNotFoundError(f"{xml_file_name} not found in {self.freecad_file}")

            with z.open(xml_file_name) as xml_file:
                tree = parse(xml_file)
                root = tree.getroot()
                if xml_file_name == "Document.xml":
                    self.original_version = self.extract_version_from_xml(root)
                return root

    @staticmethod
    def extract_version_from_xml(root: Element) -> Version:
        doc_version = root.attrib.get("ProgramVersion")
        if doc_version is None:
            raise ValueError("document.xml does not contain a ProgramVersion attribute")

        raw = doc_version.strip()

        try:
            return Version(raw)
        except InvalidVersion:
            pass

        # Try to handle known custom form: e.g., "1.1R42542 (Git)"
        # Pattern: major.minor 'R' buildnumber, e.g., 1.1R42542
        match = re.match(r"^(\d+)\.(\d+)R(\d+)", raw)
        if match:
            major, minor, build = match.groups()
            reformatted = f"{major}.{minor}.{build}"
            return Version(reformatted)

        # Try to extract something vaguely version-like - remove parentheses/suffixes and retry
        stripped = re.split(r"[^\w.-]+", raw)[0]
        try:
            return Version(stripped)
        except InvalidVersion:
            raise ValueError(f"Unrecognized ProgramVersion format: {raw}")

    def run_forward_migration(self):
        for migrator in self.migrators:
            if self.original_version < migrator.changed_in_freecad_version:
                print(f"Running forward migration {migrator.name}...")
                migrator().forward(self.document_xml, self.gui_document_xml)

    def run_backward_migration(self):
        for migrator in reversed(self.migrators):
            if self.original_version > migrator.changed_in_freecad_version:
                print(f"Running backward migration {migrator.name}...")
                migrator().backward(self.document_xml, self.gui_document_xml)

    def export(self, filename: str):
        """Write the modified FCStd file to the given file."""

        # Update the version strings
        self.document_xml.set("ProgramVersion", str(self.target_version))
        self.gui_document_xml.set("ProgramVersion", str(self.target_version))

        with zipfile.ZipFile(filename, "a") as outfile:
            outfile.writestr("Document.xml", tostring(self.document_xml, encoding="utf-8"))
            outfile.writestr("GuiDocument.xml", tostring(self.gui_document_xml, encoding="utf-8"))
            with zipfile.ZipFile(self.freecad_file, "r") as z:
                for item in z.namelist():
                    if item not in ("Document.xml", "GuiDocument.xml"):
                        outfile.writestr(item, z.read(item))
