# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
Unit tests for the MarkdownMerge module.

"""

import unittest
import unittest.mock
import os
import re
import sys
from mdMerge.markdownMerge import CLI

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
        super().__init__(*args)
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
        path = path.replace("~", self.tempDirPath.name)
        return path

    # -------------------------------------------------------------------------+
    # setup, teardown, noop
    # -------------------------------------------------------------------------+

    def setUp(self):
        """Create data used by the test cases.

        """

        import tempfile

        self.tempDirPath = tempfile.TemporaryDirectory()
        return

    def tearDown(self):
        """Cleanup data used by the test cases.

        """

        import tempfile

        self.tempDirPath.cleanup()
        self.tempDirPath = None

    def testNoOp(self):
        """Excercise tearDown and setUp methods.

        This test does nothing itself. It is useful to test the tearDown()
        and setUp() methods in isolation (without side effects).

        """
        return

    # -------------------------------------------------------------------------+
    # tests for CLI.ParseCommandArgs()
    # -------------------------------------------------------------------------+

    def testParseVersion(self):
        """Test CLI.ParseCommandArgs().

        Happy path '--version' argument.

        """

        cut = CLI()
        args = ("--version",)
        cut.ParseCommandArgs(args)
        self.assertTrue(cut.args.showVersion)

    def testParseVersionInvalidArgs(self):
        """Test CLI.ParseCommandArgs().

        '--version' argument, with extra invalid stuff.

        """

        args = ("--version", "-x")
        with self.assertRaises(SystemExit):
            with CoreCLITests.RedirectStdStreams(
                stdout=self.devnull, stderr=self.devnull):
                cut = CLI()
                cut.ParseCommandArgs(args)

    # -------------------------------------------------------------------------+
    # test for CLI.Execute()
    # -------------------------------------------------------------------------+

    # merge tests
    #

    @unittest.mock.patch('os.path.expanduser')
    def testNoIncludes(self, mock_expanduser):
        """Test CLI.Execute()

        Make certain the file is not modified when there are no includes.

        """


        mock_expanduser.side_effect = lambda x: self._SideEffectExpandUser(x)
        rwMock = unittest.mock.MagicMock()
        inputFilePath = os.path.join(self.__dataDir, "no-include.mmd")
        outputFilePath = os.path.join(self.tempDirPath.name, "out.mmd")

        cut = CLI(stdin=rwMock, stdout=rwMock)
        args = ("-o", outputFilePath, inputFilePath)
        cut.ParseCommandArgs(args)
        rwMock.reset_mock()
        cut.Execute()
        self.assertTrue(self._AreFilesIdentical(
            inputFilePath, outputFilePath))


    # miscellaneous tests
    #

    @unittest.mock.patch('os.path.expanduser')
    def testShowVersion(self, mock_expanduser):
        """Test CLI.Execute()

        Make certain the --version option produces correct output.

        """

        import os.path
        import mdMerge

        mock_expanduser.side_effect = lambda x: self._SideEffectExpandUser(x)
        rwMock = unittest.mock.MagicMock()
        cut = CLI(stdin=rwMock, stdout=rwMock)
        args = ("--version", )
        cut.ParseCommandArgs(args)
        rwMock.reset_mock()
        cut.Execute()
        calls = [
            unittest.mock.call.write(
                "mdmerge version {0}".format(mdMerge.__version__)),
            unittest.mock.call.write("\n")]
        rwMock.assert_has_calls(calls)
        self.assertEqual(2, rwMock.write.call_count)
