# SPDX-License-Identifier: LGPL-2.1-or-later

import sys
import tempfile
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock
import pathlib
from freecad.fcstdmigrator import discover


class TestDiscover(TestCase):

    def setUp(self):
        self.tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.tmpdir_obj.name)
        self._original_sys_path = sys.path.copy()
        sys.path.insert(0, str(self.tmp_path))
        (self.tmp_path / "fake_migrator_base.py").write_text("class Migrator: pass")

    def tearDown(self):
        sys.path[:] = self._original_sys_path
        self.tmpdir_obj.cleanup()

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.rglob")
    @patch("pathlib.Path.resolve")
    def test_discover_ignores_dunder_files(self, mock_resolve, mock_glob, mock_is_file):
        base_dir = pathlib.Path("/freecad/fcstdmigrator/migrations").resolve()
        mock_resolve.return_value = base_dir

        mock_is_file.return_value = True
        mock_glob.return_value = [
            base_dir / "__init__.py",
            base_dir / "__pycache__",
        ]

        result = discover.find_migrator_subclasses("migrations")

        self.assertEqual(len(result), 0)

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.rglob")
    @patch("pathlib.Path.resolve")
    def test_discover_ignores_non_py_files(self, mock_resolve, mock_glob, mock_is_file):
        base_dir = pathlib.Path("/freecad/fcstdmigrator/migrations").resolve()
        mock_resolve.return_value = base_dir

        mock_is_file.return_value = True
        mock_glob.return_value = [
            base_dir / "main.cpp",
            base_dir / "LICENSE",
            base_dir / "README.md",
            base_dir / "requirements.txt",
        ]

        result = discover.find_migrator_subclasses("migrations")

        self.assertEqual(len(result), 0)

    def test_finds_migrator_subclasses_in_nested_modules(self):
        # Create directory structure
        pkg_dir = self.tmp_path / "mypkg" / "sub"
        pkg_dir.mkdir(parents=True)

        subclass_code = """
from fake_migrator_base import Migrator
class MyMigrator(Migrator):
    pass
"""
        (pkg_dir / "my_migrator.py").write_text(subclass_code)

        from fake_migrator_base import Migrator as FakeMigrator

        with mock.patch.object(discover, "Migrator", FakeMigrator):
            result = discover.find_migrator_subclasses(str(self.tmp_path / "mypkg"))

        names = {cls.__name__ for cls in result}

        self.assertIn("MyMigrator", names)
        self.assertTrue(all(issubclass(c, FakeMigrator) for c in result))

    def test_ignores_non_migrator_classes(self):
        code = """
from fake_migrator_base import Migrator
class NotAMigrator: pass
"""
        (self.tmp_path / "not_a_migrator.py").write_text(code)

        from freecad.fcstdmigrator.discover import find_migrator_subclasses

        result = find_migrator_subclasses(str(self.tmp_path))
        self.assertEqual(result, [])

    def test_fallback_spec_from_file_location(self):
        test_file = self.tmp_path / "my_migrator.py"
        test_file.write_text(
            """
from fake_migrator_base import Migrator
class FallbackMigrator(Migrator): pass
"""
        )
        from fake_migrator_base import Migrator as FakeMigrator

        # Patch importlib.util.find_spec to always return None
        with mock.patch.object(discover, "Migrator", FakeMigrator):
            with mock.patch("importlib.util.find_spec", return_value=None):
                from freecad.fcstdmigrator.discover import find_migrator_subclasses

                result = find_migrator_subclasses(str(self.tmp_path))

        names = {cls.__name__ for cls in result}
        self.assertIn("FallbackMigrator", names)
