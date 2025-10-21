# SPDX-License-Identifier: LGPL-2.1-or-later

import unittest
from unittest import mock
import tempfile
import zipfile
import pathlib
from xml.etree.ElementTree import Element, fromstring
from packaging.version import Version

from freecad.formatmigrator.migrate import Migrate


class TestExtractVersion(unittest.TestCase):
    def test_extract_version_from_xml_valid_formats(self):
        # Simple
        root = Element("Document", ProgramVersion="1.2.3")
        v = Migrate.extract_version_from_xml(root)
        self.assertEqual(v, Version("1.2.3"))

        # FreeCAD-style "1.1R42542 (Git)"
        root = Element("Document", ProgramVersion="1.1R42542 (Git)")
        v = Migrate.extract_version_from_xml(root)
        self.assertEqual(v, Version("1.1.42542"))

        # With recognized beta string
        root = Element("Document", ProgramVersion="2.0beta")
        v = Migrate.extract_version_from_xml(root)
        self.assertEqual(Version("2.0b0"), v)

    def test_extract_version_from_xml_invalid(self):
        root = Element("Document", ProgramVersion="nonsense")
        with self.assertRaises(ValueError):
            Migrate.extract_version_from_xml(root)


class TestLoadXML(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.freecad_file = pathlib.Path(self.tmpdir.name) / "sample.FCStd"
        self.doc_xml = b'<Document ProgramVersion="1.0"><Root/></Document>'
        self.gui_xml = b"<GuiDocument/>"
        with zipfile.ZipFile(self.freecad_file, "w") as z:
            z.writestr("Document.xml", self.doc_xml)
            z.writestr("GuiDocument.xml", self.gui_xml)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load_xml_reads_document_and_sets_original_version(self):
        m = Migrate.__new__(Migrate)
        m.freecad_file = str(self.freecad_file)
        root = m.load_xml("Document.xml")
        self.assertEqual(root.tag, "Document")
        self.assertEqual(str(m.original_version), "1.0")

    def test_load_xml_raises_when_missing_file(self):
        m = Migrate.__new__(Migrate)
        m.freecad_file = str(self.freecad_file)
        with self.assertRaises(FileNotFoundError):
            m.load_xml("Nonexistent.xml")


class TestMigrationLogic(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.freecad_file = pathlib.Path(self.tmpdir.name) / "test.FCStd"
        with zipfile.ZipFile(self.freecad_file, "w") as z:
            z.writestr("Document.xml", '<Document ProgramVersion="1.0"/>')
            z.writestr("GuiDocument.xml", "<GuiDocument/>")

    def tearDown(self):
        self.tmpdir.cleanup()

    def make_mock_migrator(self, name, version):
        cls = mock.Mock()
        cls.name = name
        cls.changed_in_freecad_version = Version(version)
        cls.date = version
        cls.return_value.forward = mock.Mock()
        cls.return_value.backward = mock.Mock()
        return cls

    @mock.patch("freecad.formatmigrator.migrate.find_migrator_subclasses")
    def test_runs_forward_or_backward_correctly(self, mock_find):
        forward = self.make_mock_migrator("Forward", "2.0")
        backward = self.make_mock_migrator("Backward", "0.5")
        mock_find.return_value = [forward, backward]

        # Target higher than original -> forward migration
        Migrate(str(self.freecad_file), Version("2.0"))
        forward.return_value.forward.assert_called()
        backward.return_value.backward.assert_not_called()

        # Target lower than original -> backward migration
        forward.return_value.forward.reset_mock()
        backward.return_value.backward.reset_mock()
        Migrate(str(self.freecad_file), Version("0.5"))
        backward.return_value.backward.assert_called()
        forward.return_value.forward.assert_not_called()


class TestExport(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.freecad_file = pathlib.Path(self.tmpdir.name) / "src.FCStd"
        self.out_file = pathlib.Path(self.tmpdir.name) / "out.FCStd"
        doc_xml = b'<Document ProgramVersion="1.0"/>'
        gui_xml = b'<GuiDocument ProgramVersion="1.0"/>'
        with zipfile.ZipFile(self.freecad_file, "w") as z:
            z.writestr("Document.xml", doc_xml)
            z.writestr("GuiDocument.xml", gui_xml)
            z.writestr("Extra.dat", b"extra")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_export_updates_and_writes_files(self):
        m = Migrate.__new__(Migrate)
        m.freecad_file = str(self.freecad_file)
        m.target_version = Version("2.0")
        m.document_xml = Element("Document", ProgramVersion="1.0")
        m.gui_document_xml = Element("GuiDocument", ProgramVersion="1.0")

        m.export(str(self.out_file))

        with zipfile.ZipFile(self.out_file, "r") as z:
            files = z.namelist()
            self.assertIn("Document.xml", files)
            self.assertIn("GuiDocument.xml", files)
            doc = fromstring(z.read("Document.xml"))
            self.assertEqual(doc.attrib["ProgramVersion"], "2.0")
