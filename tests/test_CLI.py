# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
Unit tests for the cli module, CLI class.

"""

from __future__ import print_function, with_statement, generators, \
    unicode_literals
import unittest
import mock
import os
import os.path
import re
import sys
from mdmerge.cli import CLI

import pprint

class CoreCLITests(unittest.TestCase):

    class RedirectStdStreams:
        """A context manager that can temporarily redirect the standard
        streams.

        """

        def __init__(self, stdout=None, stderr=None):
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


    # NOTE: many of theses tests use a mock for expanduser to change the
    #       default location of the data file to a temporary directory so
    #       that the unit tests do not trash the hotp.data file of the user
    #       running the tests.
    #
    # NOTE: some of these tests use a mock for _getKeyStretches to force a much
    #       faster key stretch algorithm than is used in the normal execution
    #       mode. This is done so the unit tests are fast and developers won't
    #       be tempted to bypass the (otherwise slow) tests.
    #

    def __init__(self, *args):
        self.devnull = open(os.devnull, "w")
        unittest.TestCase.__init__(self, *args)
        self.__root = os.path.dirname(__file__)
        self.__dataDir = os.path.join(self.__root, "data")

    def _AreFilesIdentical(self, filePathA, filePathB):

        import difflib

        fileTextA = open(filePathA).read().splitlines(True)
        fileTextB = open(filePathB).read().splitlines(True)
        difference = list(difflib.context_diff(fileTextA, fileTextB, n=1))
        diffLineCount = len(difference)
        if 0 == diffLineCount:
            return True;
        pprint.pprint(difference)
        return False;

    def _SideEffectExpandUser(self, path):
        if not path.startswith("~"):
            return path
        path = path.replace("~", self.tempDirPath)
        return path

    # -------------------------------------------------------------------------+
    # setup, teardown, noop
    # -------------------------------------------------------------------------+

    def setUp(self):
        """Create data used by the test cases.

        """

        import tempfile

        self.tempDirPath = tempfile.mkdtemp()
        return

    def tearDown(self):
        """Cleanup data used by the test cases.

        """

        import shutil

        if None != self.tempDirPath:
            shutil.rmtree(self.tempDirPath)
            self.tempDirPath = None

    def testNoOp(self):
        """Excercise tearDown and setUp methods.

        This test does nothing itself. It is useful to test the tearDown()
        and setUp() methods in isolation (without side effects).

        """
        return

    # -------------------------------------------------------------------------+
    # tests for CLI.parseCommandArgs()
    # -------------------------------------------------------------------------+

    def testParseExportTargetHtml(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        tgt = "html"
        expectedExt = "." + tgt;
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandonCLI)
        self.assertTrue(cut._CLI__useStdin)
        self.assertTrue(cut._CLI__useStdout)
        self.assertIsNone(cut._CLI__outFilepath)
        self.assertEqual(1, len(cut._CLI__inputFilepaths))
        self.assertFalse(cut._CLI__bookTxtIsSpecial)
        self.assertEqual(expectedExt, cut._CLI__wildcardExtensionIs)
        self.assertFalse(cut._CLI__stdinIsBook)

    def testParseExportTargetInvalid(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        args = ("--export-target", "wat", "-")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    def testParseExportTargetLatex(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        tgt = "latex"
        expectedExt = ".tex";
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expectedExt, cut._CLI__wildcardExtensionIs)

    def testParseExportTargetLyx(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        tgt = "lyx"
        expectedExt = "." + tgt;
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expectedExt, cut._CLI__wildcardExtensionIs)

    def testParseExportTargetOdf(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        tgt = "odf"
        expectedExt = "." + tgt;
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expectedExt, cut._CLI__wildcardExtensionIs)

    def testParseExportTargetOpml(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        tgt = "opml"
        expectedExt = "." + tgt;
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expectedExt, cut._CLI__wildcardExtensionIs)

    def testParseExportTargetRtf(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        tgt = "rtf"
        expectedExt = "." + tgt;
        args = ("--export-target", tgt, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual(tgt, cut.args.exportTarget)
        self.assertEqual(expectedExt, cut._CLI__wildcardExtensionIs)

    def testParseLeanpub(self):
        """Test CLI.parseCommandArgs().

        Specifying special treatment of book.txt file.

        """

        cut = CLI()
        args = ("--leanpub", "-")
        cut.parseCommandArgs(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertTrue(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandonCLI)
        self.assertTrue(cut._CLI__useStdin)
        self.assertTrue(cut._CLI__useStdout)
        self.assertIsNone(cut._CLI__outFilepath)
        self.assertEqual(1, len(cut._CLI__inputFilepaths))
        self.assertTrue(cut._CLI__bookTxtIsSpecial)
        self.assertEqual(".html", cut._CLI__wildcardExtensionIs)
        self.assertFalse(cut._CLI__stdinIsBook)

    def testParseLeanpubOnly(self):
        """Test CLI.parseCommandArgs().

        Specify leanpub flag but no other flags or args.
        Expecting an error.

        """

        args = ("--leanpub")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    def testParseOneInputFile(self):
        """Test CLI.parseCommandArgs().

        Happy path. A single input file with no optional arguments.

        """

        cut = CLI()
        args = ("tests/data/a.mmd")
        cut.parseCommandArgs(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("tests/data/a.mmd", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandonCLI)
        self.assertFalse(cut._CLI__useStdin)
        self.assertTrue(cut._CLI__useStdout)
        self.assertIsNone(cut._CLI__outFilepath)
        self.assertEqual(1, len(cut._CLI__inputFilepaths))
        self.assertFalse(cut._CLI__bookTxtIsSpecial)
        self.assertEqual(".html", cut._CLI__wildcardExtensionIs)
        self.assertFalse(cut._CLI__stdinIsBook)

    def testParseOutfileAndStdin(self):
        """Test CLI.parseCommandArgs().

        Using stdin and an output file.

        """

        ofilepath = os.path.join(self.tempDirPath, "x.html")
        args = ("-o", ofilepath, "-")
        cut = CLI()
        cut.parseCommandArgs(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertEqual(ofilepath, cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandonCLI)
        self.assertTrue(cut._CLI__useStdin)
        self.assertFalse(cut._CLI__useStdout)
        self.assertEqual(ofilepath, cut._CLI__outFilepath)
        self.assertEqual(1, len(cut._CLI__inputFilepaths))
        self.assertFalse(cut._CLI__bookTxtIsSpecial)
        self.assertEqual(".html", cut._CLI__wildcardExtensionIs)
        self.assertFalse(cut._CLI__stdinIsBook)

    def testParseOutWithNoFile(self):
        """Test CLI.parseCommandArgs().

        Using an output file but ambigous about whether
        token after output flag is an out file or an in file.
        Expecting an error.

        """

        args = ("-o", "tests/data/a.mmd")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    def testParseOutWithNoFileJustStdin(self):
        """Test CLI.parseCommandArgs().

        Using stdin alone. Expecting an error.

        """

        args = ("-o", "-")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    def testParseStdin(self):
        """Test CLI.parseCommandArgs().

        Happy path. Using stdin instead of input files.

        """

        cut = CLI()
        args = ("-")
        cut.parseCommandArgs(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertFalse(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandonCLI)
        self.assertTrue(cut._CLI__useStdin)
        self.assertTrue(cut._CLI__useStdout)
        self.assertIsNone(cut._CLI__outFilepath)
        self.assertEqual(1, len(cut._CLI__inputFilepaths))
        self.assertFalse(cut._CLI__bookTxtIsSpecial)
        self.assertEqual(".html", cut._CLI__wildcardExtensionIs)
        self.assertFalse(cut._CLI__stdinIsBook)
        self.assertFalse(cut._CLI__stdinIsBook)

    def testParseStdinIsIndex(self):
        """Test CLI.parseCommandArgs().

        Specifying stdin should be treated as an index file (a book file).

        """

        cut = CLI()
        args = ("--book", "-")
        cut.parseCommandArgs(args)
        self.assertEqual("html", cut.args.exportTarget)
        self.assertEqual(1, len(cut.args.inFiles))
        self.assertEqual("-", cut.args.inFiles[0])
        self.assertFalse(cut.args.leanPub)
        self.assertIsNone(cut.args.outFile)
        self.assertFalse(cut.args.showVersion)
        self.assertTrue(cut.args.forceBook)

        self.assertFalse(cut._CLI__abandonCLI)
        self.assertTrue(cut._CLI__useStdin)
        self.assertTrue(cut._CLI__useStdout)
        self.assertIsNone(cut._CLI__outFilepath)
        self.assertEqual(1, len(cut._CLI__inputFilepaths))
        self.assertFalse(cut._CLI__bookTxtIsSpecial)
        self.assertEqual(".html", cut._CLI__wildcardExtensionIs)
        self.assertTrue(cut._CLI__stdinIsBook)

    def testParseStdinPlusOthers(self):
        """Test CLI.parseCommandArgs().

        Using stdin as well as a list of input files. Expecting
        an error.

        """

        args = ("-", "tests/data/a.mmd")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    def testParseUnrecognizedArg(self):
        """Test CLI.parseCommandArgs().

        Specify unrecognized flag.
        Expecting an error.

        """

        args = ("--wat", "-")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    def testParseVersion(self):
        """Test CLI.parseCommandArgs().

        Happy path '--version' argument.

        """

        cut = CLI()
        args = ("--version",)
        cut.parseCommandArgs(args)
        self.assertTrue(cut.args.showVersion)

    def testParseVersionInvalidArgs(self):
        """Test CLI.parseCommandArgs().

        '--version' argument, with extra invalid stuff.

        """

        args = ("--version", "-x")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.parseCommandArgs(args)

    # -------------------------------------------------------------------------+
    # test for CLI.Execute()
    # -------------------------------------------------------------------------+

    # merge tests
    #

    @mock.patch('os.path.expanduser')
    def xtestNoIncludes(self, mock_expanduser):
        """Test CLI.Execute()

        Make certain the file is not modified when there are no includes.

        """


        mock_expanduser.side_effect = lambda x: self._SideEffectExpandUser(x)
        rwMock = mock.MagicMock()
        inputFilePath = os.path.join(self.__dataDir, "no-include.mmd")
        outputFilePath = os.path.join(self.tempDirPath, "out.mmd")

        cut = CLI(stdin=rwMock, stdout=rwMock)
        args = ("-o", outputFilePath, inputFilePath)
        cut.parseCommandArgs(args)
        rwMock.reset_mock()
        cut.Execute()
        self.assertTrue(self._AreFilesIdentical(
            inputFilePath, outputFilePath))


    # miscellaneous tests
    #

    @mock.patch('os.path.expanduser')
    def xtestShowVersion(self, mock_expanduser):
        """Test CLI.Execute()

        Make certain the --version option produces correct output.

        """

        import os.path
        import mdMerge

        mock_expanduser.side_effect = lambda x: self._SideEffectExpandUser(x)
        rwMock = mock.MagicMock()
        cut = CLI(stdin=rwMock, stdout=rwMock)
        args = ("--version", )
        cut.parseCommandArgs(args)
        rwMock.reset_mock()
        cut.Execute()
        calls = [
            mock.call.write(
                "mdmerge version {0}".format(mdMerge.__version__)),
            mock.call.write("\n")]
        rwMock.assert_has_calls(calls)
        self.assertEqual(2, rwMock.write.call_count)


#eof