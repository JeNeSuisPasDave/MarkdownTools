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
from mdmerge.merge import MarkdownMerge
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
    # tests for MarkdownMerge.merge()
    # -------------------------------------------------------------------------+

    def testEmptyInput(self):
        """Test MarkdownMerge.merge().

        Happy path '--version' argument.

        """

        cut = MarkdownMerge(".html")
        inFilePath = os.path.join(self.__dataDir, "empty.mmd")
        inFileNode = Node(inFilePath)
        cut.merge(inFileNode, sys.stdout)
