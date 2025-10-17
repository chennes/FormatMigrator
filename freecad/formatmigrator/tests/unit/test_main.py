# SPDX-License-Identifier: LGPL-2.1-or-later

from unittest import TestCase
from unittest.mock import patch
import pathlib
from freecad.formatmigrator import main


class TestMain(TestCase):

    def setUp(self):
        self.test_input = pathlib.Path("test.FCStd")
        self.test_output = pathlib.Path("output.FCStd")
        self.test_version = "0.20"

    def tearDown(self):
        pass

    @patch("pathlib.Path.is_file")
    def test_parse_args_valid_input(self, mock_is_file):
        mock_is_file.return_value = True
        test_args = [
            "prog",
            "-i",
            str(self.test_input),
            "-o",
            str(self.test_output),
            "-v",
            self.test_version,
        ]
        with patch("sys.argv", test_args):
            args = main.parse_args()
            self.assertEqual(args.input, self.test_input)
            self.assertEqual(args.output, self.test_output)
            self.assertEqual(args.version, self.test_version)

    @patch("pathlib.Path.is_file")
    def test_parse_args_missing_file(self, mock_is_file):
        mock_is_file.return_value = False
        test_args = [
            "prog",
            "-i",
            "nonexistent.FCStd",
            "-o",
            str(self.test_output),
            "-v",
            self.test_version,
        ]
        with patch("sys.argv", test_args):
            with self.assertRaises(FileNotFoundError):
                main.parse_args()

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    @patch("builtins.input")
    def test_parse_args_existing_output_rejected(self, mock_input, mock_exists, mock_is_file):
        mock_is_file.return_value = True
        mock_exists.return_value = True
        mock_input.return_value = "n"
        test_args = [
            "prog",
            "-i",
            str(self.test_input),
            "-o",
            str(self.test_output),
            "-v",
            self.test_version,
        ]
        with patch("sys.argv", test_args):
            with self.assertRaises(SystemExit):
                main.parse_args()

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    @patch("builtins.input")
    def test_parse_args_existing_output_confirmed(self, mock_input, mock_exists, mock_is_file):
        mock_is_file.return_value = True
        mock_exists.return_value = True
        mock_input.return_value = "y"
        test_args = [
            "prog",
            "-i",
            str(self.test_input),
            "-o",
            str(self.test_output),
            "-v",
            self.test_version,
        ]
        with patch("sys.argv", test_args):
            args = main.parse_args()
            self.assertEqual(args.input, self.test_input)
            self.assertEqual(args.output, self.test_output)
            self.assertEqual(args.version, self.test_version)
