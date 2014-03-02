# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
Unit tests for the MarkdownMerge module, MarkdownMerge class.

"""

import unittest
import unittest.mock
import os
import os.path
import re
import sys
import io
from mdmerge.markdownMerge import MarkdownMerge
from mdmerge.node import Node

import pprint

class MarkdownMergeTests(unittest.TestCase):

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

        with io.open(filePathA) as fileA, \
        io.open(filePathB) as fileB:
            fileTextA = fileA.read().splitlines(True)
            fileTextB = fileB.read().splitlines(True)
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
    # tests for MarkdownMerge.merge()
    # -------------------------------------------------------------------------+

    def testEmptyInput(self):
        """Test MarkdownMerge.merge().

        A zero length file should produce a zero length output.

        """

        infilePath = os.path.join(self.__dataDir, "empty.mmd")
        outfilePath = os.path.join(self.tempDirPath.name, "result.mmd")
        errfilePath = os.path.join(self.tempDirPath.name, "result.err")
        with io.open(outfilePath, "w") as outfile, \
            io.open(errfilePath, "w") as errfile, \
            MarkdownMergeTests.RedirectStdStreams(
                stdout=outfile, stderr=errfile):
            cut = MarkdownMerge(".html")
            infileNode = Node(infilePath)
            cut.merge(infileNode, sys.stdout)
        self.assertEqual(0, os.stat(outfilePath).st_size)
        self.assertEqual(0, os.stat(errfilePath).st_size)

    def testNoIncludes(self):
        """Test MarkdownMerge.merge().

        A file with no includes should produce an identical file.

        """

        infilePath = os.path.join(self.__dataDir, "aa.mmd")
        expectedSize = os.stat(infilePath).st_size
        outfilePath = os.path.join(self.tempDirPath.name, "result.mmd")
        errfilePath = os.path.join(self.tempDirPath.name, "result.err")
        with io.open(outfilePath, "w") as outfile, \
            io.open(errfilePath, "w") as errfile, \
            MarkdownMergeTests.RedirectStdStreams(
                stdout=outfile, stderr=errfile):
            cut = MarkdownMerge(".html")
            infileNode = Node(infilePath)
            cut.merge(infileNode, sys.stdout)
        self.assertEqual(expectedSize, os.stat(outfilePath).st_size)
        self.assertEqual(0, os.stat(errfilePath).st_size)

    def testSingleIncludeMarked(self):
        """Test MarkdownMerge.merge().

        A file with one Marked include.

        """

        infilePath = os.path.join(self.__dataDir, "a.mmd")
        expectedfilePath = os.path.join(self.__dataDir, "expected-a.mmd")
        expectedSize = os.stat(expectedfilePath).st_size
        outfilePath = os.path.join(self.tempDirPath.name, "result.mmd")
        errfilePath = os.path.join(self.tempDirPath.name, "result.err")
        with io.open(outfilePath, "w") as outfile, \
            io.open(errfilePath, "w") as errfile, \
            MarkdownMergeTests.RedirectStdStreams(
                stdout=outfile, stderr=errfile):
            cut = MarkdownMerge(".html")
            infileNode = Node(infilePath)
            cut.merge(infileNode, sys.stdout)
        self.assertEqual(expectedSize, os.stat(outfilePath).st_size)
        self.assertEqual(0, os.stat(errfilePath).st_size)
        self._AreFilesIdentical(expectedfilePath, outfilePath)
