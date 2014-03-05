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

    def __init__(self, *args):
        self.devnull = open(os.devnull, "w")
        super().__init__(*args)
        self.__root = os.path.dirname(__file__)
        self.__dataDir = os.path.join(self.__root, "data")

    def _areFilesIdentical(self, filePathA, filePathB):

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

    def _mergeTest(self, infilePath, expectedfilePath=None):
        """Take a single inputfile and produce a merged output file, then
        check the results against a file containing the expected content.

        Args:
            infilePath: the input file path, relative to self.__dataDir
            expectedFilePath: the expected file path, relative to
                self.__dataDir. Defaults to None.

        """

        infilePath = os.path.join(self.__dataDir, infilePath)
        if None != expectedfilePath:
            expectedfilePath = os.path.join(self.__dataDir, expectedfilePath)
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
        self.assertEqual(0, os.stat(errfilePath).st_size)
        if None != expectedfilePath:
            self.assertEqual(expectedSize, os.stat(outfilePath).st_size)
            self.assertTrue(self._areFilesIdentical(
                expectedfilePath, outfilePath))

    def _mergeTry(self, infilePath, expectedfilePath):
        """Take a single inputfile and produce a merged output file, then
        dump the output to stdout.

        Args:
            infilePath: the input file path, relative to self.__dataDir
            expectedFilePath: the expected file path, relative to
                self.__dataDir

        """

        infilePath = os.path.join(self.__dataDir, infilePath)
        expectedfilePath = os.path.join(self.__dataDir, expectedfilePath)
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
        with io.open(outfilePath, "r") as outfile:
            for line in outfile:
                print(line, end='')
        if 0 != os.stat(errfilePath).st_size:
            with io.open(errfilePath, "r") as errfile:
                for line in errfile:
                    print(line, end='')

    def _sideEffectExpandUser(self, path):
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

        self._mergeTest("aa.mmd", "aa.mmd")

    def testSingleIncludeFencedTransclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence.

        """

        self._mergeTest("t-c.mmd", "expected-t-c.mmd")

    def testSingleIncludeLeanpubCode(self):
        """Test MarkdownMerge.merge().

        A file with one leanpub include specification.

        """

        self._mergeTest("lp-a.mmd", "expected-lp-a.mmd")

    def testSingleIncludeLeanpubTitledCode(self):
        """Test MarkdownMerge.merge().

        A file with one titled leanpub include specification.

        """

        self._mergeTest("lpt-a.mmd", "expected-lpt-a.mmd")

    def testSingleIncludeMarked(self):
        """Test MarkdownMerge.merge().

        A file with one Marked include.

        """

        self._mergeTest("a.mmd", "expected-a.mmd")

    def testSingleIncludeNamedFencedTransclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside a named code fence.

        """

        self._mergeTest("t-c-named.mmd", "expected-t-c-named.mmd")

    def testSingleIncludeTransclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion.

        """

        self._mergeTest("t-a.mmd", "expected-t-a.mmd")

    def testChildToParentCycle(self):
        """Test MarkdownMerge.merge().

        A child include file that includes its parent.

        """
        with self.assertRaises(AssertionError):
            self._mergeTest("cycle-a.mmd")

    def testChildToAncestorCycle(self):
        """Test MarkdownMerge.merge().

        A deep child include file that includes an ancestor
        a couple parents away.

        """
        with self.assertRaises(AssertionError):
            self._mergeTest("cycle-b.mmd")
