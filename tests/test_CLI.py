# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""Unit tests for the CLI class of of the mdmerge module."""

from __future__ import print_function, with_statement, generators, \
    unicode_literals
import unittest
import mock
import io
import os
import os.path
import sys
from mdmerge.cli import CLI

import pprint


class CLITests(unittest.TestCase):

    """Unit tests for the cli.py module."""

    class RedirectStdStreams:

        """A context manager for standard streams.

        A context manager that can temporarily redirect the standard
        streams.

        """

        def __init__(self, stdout=None, stderr=None):
            """Constructor."""
            self._stdout = stdout or sys.stdout
            self._stderr = stderr or sys.stderr

        def __enter__(self):
            self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
            self.old_stdout.flush()
            self.old_stderr.flush()
            sys.stdout, sys.stderr = self._stdout, self._stderr

        def __exit__(self, exc_type, exc_value, traceback):
            self._stdout.flush()
            self._stderr.flush()
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr

    def __init__(self, *args):
        """Constructor."""
        self.devnull = open(os.devnull, "w")
        unittest.TestCase.__init__(self, *args)
        self.__root = os.path.dirname(__file__)
        self.__dataDir = os.path.join(self.__root, "data")

    def __del__(self):
        """Destructor."""
        self.devnull.close()
        self.devnull = None

    def _are_files_identical(self, file_path_a, file_path_b):

        import difflib

        with io.open(file_path_a) as file_a, \
                io.open(file_path_b) as file_b:
            file_text_a = file_a.read().splitlines(True)
            file_text_b = file_b.read().splitlines(True)
        difference = list(difflib.context_diff(file_text_a, file_text_b, n=1))
        diff_line_count = len(difference)
        if 0 == diff_line_count:
            return True
        pprint.pprint(difference)
        return False

    # -------------------------------------------------------------------------+
    # setup, teardown, noop
    # -------------------------------------------------------------------------+

    def setUp(self):
        """Create data used by the test cases."""
        import tempfile

        self.temp_dir_path = tempfile.mkdtemp()
        return

    def tearDown(self):
        """Cleanup data used by the test cases."""
        import shutil

        if None != self.temp_dir_path:
            shutil.rmtree(self.temp_dir_path)
            self.temp_dir_path = None

    def test_no_op(self):
        """Excercise tearDown and setUp methods.

        This test does nothing itself. It is useful to test the tearDown()
        and setUp() methods in isolation (without side effects).

        """
        return

    # -------------------------------------------------------------------------+
    # tests for CLI.parse_command_args()
    # -------------------------------------------------------------------------+

    def test_parse_export_target_html(self):
        """Test CLI.parse_command_args().

        Specify html as the export target and be certain
        the properties are set correctly.

        """
        tgt = "html"
        expected_ext = "." + tgt
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)
        self.assertFalse(cut.args.ignoreTransclusions)
        self.assertFalse(cut.args.justRaw)

        self.assertFalse(cut._CLI__abandon_cli)
        self.assertTrue(cut._CLI__use_stdin)
        self.assertTrue(cut._CLI__use_stdout)
        self.assertIsNone(cut._CLI__out_filepath)
        self.assertEqual(1, len(cut._CLI__input_filepaths))
        self.assertFalse(cut._CLI__book_txt_is_special)
        self.assertEqual(expected_ext, cut._CLI__wildcard_extension_is)
        self.assertFalse(cut._CLI__stdin_is_book)
        self.assertFalse(cut._CLI__ignore_transclusions)
        self.assertFalse(cut._CLI__just_raw)

    def test_parse_export_target_invalid(self):
        """Test CLI.parse_command_args().

        Specify an invalid target.
        Expecting an error.

        """
        args = ("--export-target", "wat", "-")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    def test_parse_export_target_latex(self):
        """Test CLI.parse_command_args().

        Specify latex as the export target and be certain
        the properties are set correctly.

        """
        tgt = "latex"
        expected_ext = ".tex"
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expected_ext, cut._CLI__wildcard_extension_is)

    def test_parse_export_target_lyx(self):
        """Test CLI.parse_command_args().

        Specify lyx as the export target and be certain
        the properties are set correctly.

        """
        tgt = "lyx"
        expected_ext = "." + tgt
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expected_ext, cut._CLI__wildcard_extension_is)

    def test_parse_export_target_odf(self):
        """Test CLI.parse_command_args().

        Specify odf as the export target and be certain
        the properties are set correctly.

        """
        tgt = "odf"
        expected_ext = "." + tgt
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expected_ext, cut._CLI__wildcard_extension_is)

    def test_parse_export_target_opml(self):
        """Test CLI.parse_command_args().

        Specify opml as the export target and be certain
        the properties are set correctly.

        """
        tgt = "opml"
        expected_ext = "." + tgt
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expected_ext, cut._CLI__wildcard_extension_is)

    def test_parse_export_target_rtf(self):
        """Test CLI.parse_command_args().

        Specify rtf as the export target and be certain
        the properties are set correctly.

        """
        tgt = "rtf"
        expected_ext = "." + tgt
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expected_ext, cut._CLI__wildcard_extension_is)

    def test_parse_ignore_transclusions(self):
        """test CLI.parse_command_args().

        Specify that transclusions should be ignored and be certain
        the properties are set correctly.

        """
        args = ("--ignore-transclusions", "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertTrue(cut.args.ignoreTransclusions)
        self.assertTrue(cut._CLI__ignore_transclusions)

    def test_parse_just_raw(self):
        """test CLI.parse_command_args().

        Specify that only raw include specifications should be process;
        all other include specifications should be ignore. Be certain
        the properties are set correctly.

        """
        args = ("--just-raw", "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertTrue(cut.args.justRaw)
        self.assertTrue(cut._CLI__just_raw)

    def test_parse_leanpub(self):
        """Test CLI.parse_command_args().

        Specifying special treatment of book.txt file.

        """
        cut = CLI()
        args = ("--leanpub", "-")
        cut.parse_command_args(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertTrue(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandon_cli)
        self.assertTrue(cut._CLI__use_stdin)
        self.assertTrue(cut._CLI__use_stdout)
        self.assertIsNone(cut._CLI__out_filepath)
        self.assertEqual(1, len(cut._CLI__input_filepaths))
        self.assertTrue(cut._CLI__book_txt_is_special)
        self.assertEqual(".html", cut._CLI__wildcard_extension_is)
        self.assertFalse(cut._CLI__stdin_is_book)

    def test_parse_leanpub_only(self):
        """Test CLI.parse_command_args().

        Specify leanpub flag but no other flags or args.
        Expecting an error.

        """
        args = ("--leanpub")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    def test_parse_one_input_file(self):
        """Test CLI.parse_command_args().

        Happy path. A single input file with no optional arguments.

        """
        cut = CLI()
        args = ("tests/data/a.mmd")
        cut.parse_command_args(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("tests/data/a.mmd", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandon_cli)
        self.assertFalse(cut._CLI__use_stdin)
        self.assertTrue(cut._CLI__use_stdout)
        self.assertIsNone(cut._CLI__out_filepath)
        self.assertEqual(1, len(cut._CLI__input_filepaths))
        self.assertFalse(cut._CLI__book_txt_is_special)
        self.assertEqual(".html", cut._CLI__wildcard_extension_is)
        self.assertFalse(cut._CLI__stdin_is_book)

    def test_parse_outfile_and_stdin(self):
        """Test CLI.parse_command_args().

        Using stdin and an output file.

        """
        ofilepath = os.path.join(self.temp_dir_path, "x.html")
        args = ("-o", ofilepath, "-")
        cut = CLI()
        cut.parse_command_args(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertEqual(ofilepath, cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandon_cli)
        self.assertTrue(cut._CLI__use_stdin)
        self.assertFalse(cut._CLI__use_stdout)
        self.assertEqual(ofilepath, cut._CLI__out_filepath)
        self.assertEqual(1, len(cut._CLI__input_filepaths))
        self.assertFalse(cut._CLI__book_txt_is_special)
        self.assertEqual(".html", cut._CLI__wildcard_extension_is)
        self.assertFalse(cut._CLI__stdin_is_book)

    def test_parse_out_with_no_file(self):
        """Test CLI.parse_command_args().

        Using an output file but ambigous about whether
        token after output flag is an out file or an in file.
        Expecting an error.

        """
        args = ("-o", "tests/data/a.mmd")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    def test_parse_out_with_no_file_just_stdin(self):
        """Test CLI.parse_command_args().

        Using stdin alone. Expecting an error.

        """
        args = ("-o", "-")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    def test_parse_stdin(self):
        """Test CLI.parse_command_args().

        Happy path. Using stdin instead of input files.

        """
        cut = CLI()
        args = ("-")
        cut.parse_command_args(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandon_cli)
        self.assertTrue(cut._CLI__use_stdin)
        self.assertTrue(cut._CLI__use_stdout)
        self.assertIsNone(cut._CLI__out_filepath)
        self.assertEqual(1, len(cut._CLI__input_filepaths))
        self.assertFalse(cut._CLI__book_txt_is_special)
        self.assertEqual(".html", cut._CLI__wildcard_extension_is)
        self.assertFalse(cut._CLI__stdin_is_book)
        self.assertFalse(cut._CLI__stdin_is_book)

    def test_parse_stdin_is_index(self):
        """Test CLI.parse_command_args().

        Specifying stdin should be treated as an index file (a book file).

        """
        cut = CLI()
        args = ("--book", "-")
        cut.parse_command_args(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertTrue(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandon_cli)
        self.assertTrue(cut._CLI__use_stdin)
        self.assertTrue(cut._CLI__use_stdout)
        self.assertIsNone(cut._CLI__out_filepath)
        self.assertEqual(1, len(cut._CLI__input_filepaths))
        self.assertFalse(cut._CLI__book_txt_is_special)
        self.assertEqual(".html", cut._CLI__wildcard_extension_is)
        self.assertTrue(cut._CLI__stdin_is_book)

    def test_parse_stdin_plus_others(self):
        """Test CLI.parse_command_args().

        Using stdin as well as a list of input files. Expecting
        an error.

        """
        args = ("-", "tests/data/a.mmd")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    def test_parse_unrecognized_arg(self):
        """Test CLI.parse_command_args().

        Specify unrecognized flag.
        Expecting an error.

        """
        args = ("--wat", "-")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    def test_parse_version(self):
        """Test CLI.parse_command_args().

        Happy path '--version' argument.

        """
        cut = CLI()
        args = ("--version",)
        cut.parse_command_args(args)
        self.assertTrue(cut.args.showVersion)

    def test_parse_version_invalid_args(self):
        """Test CLI.parse_command_args().

        '--version' argument, with extra invalid stuff.

        """
        args = ("--version", "-x")
        with self.assertRaises(SystemExit):
            with CLITests.RedirectStdStreams(
                    stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parse_command_args(args)

    # -------------------------------------------------------------------------+
    # test for CLI.Execute()
    # -------------------------------------------------------------------------+

    # merge tests
    #

    def test_no_includes(self):
        """Test CLI.Execute().

        Make certain the file is not modified when there are no includes.

        """
        input_file_path = os.path.join(self.__dataDir, "no-include.mmd")
        output_file_path = os.path.join(self.temp_dir_path, "out.mmd")

        rw_mock = mock.MagicMock()
        cut = CLI(stdin=rw_mock, stdout=rw_mock)
        args = ("-o", output_file_path, input_file_path)
        cut.parse_command_args(args)
        rw_mock.reset_mock()
        cut.execute()
        self.assertTrue(self._are_files_identical(
            input_file_path, output_file_path))

    def test_many_input_files_with_metadata(self):
        """Test CLI.Execute().

        Make certain multiple input files are handled properly.

        """
        import shutil

        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "mmd-m-index.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-m-ch1.mmd", "book-m-ch2.mmd", "book-m-ch3.mmd",
            "book-m-end.mmd", "book-m-front.mmd", "book-m-index.mmd",
            "book-m-toc.mmd"])
        for testfilePath in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(abs_testfile_path, inputdir_path)

        expected_file_path = os.path.join(
            self.__dataDir, "expected-book-m.mmd")
        output_file_path = os.path.join(self.temp_dir_path, "out.mmd")

        rw_mock = mock.MagicMock()
        cut = CLI(stdin=rw_mock, stdout=rw_mock)
        args = ("-o", output_file_path,
                os.path.join(inputdir_path, "book-m-front.mmd"),
                os.path.join(inputdir_path, "book-m-toc.mmd"),
                os.path.join(inputdir_path, "book-m-ch1.mmd"),
                os.path.join(inputdir_path, "book-m-ch2.mmd"),
                os.path.join(inputdir_path, "book-m-ch3.mmd"),
                os.path.join(inputdir_path, "book-m-index.mmd"),
                os.path.join(inputdir_path, "book-m-end.mmd"))
        cut.parse_command_args(args)
        rw_mock.reset_mock()
        cut.execute()
        self.assertTrue(self._are_files_identical(
            expected_file_path, output_file_path))

    # miscellaneous tests
    #

    def test_show_version(self):
        """Test CLI.Execute().

        Make certain the --version option produces correct output.

        """
        import mdmerge

        rw_mock = mock.MagicMock()
        cut = CLI(stdin=rw_mock, stdout=rw_mock)
        args = ("--version", )
        cut.parse_command_args(args)
        rw_mock.reset_mock()
        cut.execute()
        calls = [
            mock.call.write(
                "mdmerge version {0}".format(mdmerge.__version__)),
            mock.call.write("\n"),
            mock.call.write(
                "Copyright 2014 Dave Hein. Licensed under MPL-2.0."),
            mock.call.write("\n")
            ]
        rw_mock.assert_has_calls(calls)
        self.assertEqual(4, rw_mock.write.call_count)

# eof
