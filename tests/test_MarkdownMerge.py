# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
Unit tests for the MarkdownMerge module, MarkdownMerge class.

"""

import unittest
import os
import os.path
import re
import sys
import io
import shutil
from mdmerge.markdownMerge import MarkdownMerge
from mdmerge.node import Node

import pprint

class MarkdownMergeTests(unittest.TestCase):

    class RedirectStdStreams:
        """A context manager that can temporarily redirect the standard
        streams.

        """

        def __init__(self, stdin=None, stdout=None, stderr=None):
            self._stdin = stdin or sys.stdin
            self._stdout = stdout or sys.stdout
            self._stderr = stderr or sys.stderr

        def __enter__(self):
            self.old_stdin, self.old_stdout, self.old_stderr = \
                sys.stdin, sys.stdout, sys.stderr
            self.old_stdout.flush()
            self.old_stderr.flush()
            sys.stdin, sys.stdout, sys.stderr = \
                self._stdin, self._stdout, self._stderr

        def __exit__(self, exc_type, exc_value, traceback):
            self._stdout.flush()
            self._stderr.flush()
            sys.stdin = self.old_stdin
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

    def _mergeTest(self,
        infilePath, expectedfilePath=None, expectingStderr=False,
        wildcardExtensionIs=".html", bookTxtIsSpecial=False,
        infileAsStdin=False, stdinIsBook=False,
        ignoreTransclusions=False, justRaw=False):
        """Take a single inputfile and produce a merged output file, then
        check the results against a file containing the expected content.

        Args:
            infilePath: the input file path, relative to self.__dataDir
            expectedFilePath: the expected file path, relative to
                self.__dataDir. Defaults to None.
            expectingStderr: if True then the stderr stream should have
                some content.
            wildcardExtensionIs: the extension to substitute if include
                file extension is a wildcardExtensionIs
            bookTxtIsSpecial: whether to treat 'book.txt' as a Leanpub index
                file.
            infileAsStdin: the CUT should access the infile via STDIN
            stdinIsBook: whether STDIN is treated as an index file
            ignoreTransclusions: whether MultiMarkdown transclusion
                specifications should be left untouched
            justRaw: whether to only process raw include specifications

        """

        # TODO: take cut constructor arguments as a dictionary argument

        infilePath = os.path.join(self.__dataDir, infilePath)
        if None != expectedfilePath:
            expectedfilePath = os.path.join(self.__dataDir, expectedfilePath)
            expectedSize = os.stat(expectedfilePath).st_size
        outfilePath = os.path.join(self.tempDirPath.name, "result.mmd")
        errfilePath = os.path.join(self.tempDirPath.name, "result.err")
        if infileAsStdin:
            with io.open(outfilePath, "w") as outfile, \
                io.open(errfilePath, "w") as errfile, \
                io.open(infilePath, "r") as infile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdin=infile, stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcardExtensionIs, bookTxtIsSpecial, stdinIsBook,
                    ignoreTransclusions, justRaw)
                infileNode = Node(os.path.dirname(infilePath))
                cut.merge(infileNode, sys.stdout)
        else:
            with io.open(outfilePath, "w") as outfile, \
                io.open(errfilePath, "w") as errfile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcardExtensionIs, bookTxtIsSpecial, stdinIsBook,
                    ignoreTransclusions, justRaw)
                infileNode = Node(filePath=infilePath)
                cut.merge(infileNode, sys.stdout)
        if expectingStderr:
            self.assertGreater(os.stat(errfilePath).st_size, 0)
        else:
            self.assertEqual(0, os.stat(errfilePath).st_size)
        if None != expectedfilePath:
            self.assertEqual(expectedSize, os.stat(outfilePath).st_size)
            self.assertTrue(self._areFilesIdentical(
                expectedfilePath, outfilePath))

    def _mergeTry(self,
        infilePath, expectedfilePath=None, expectingStderr=False,
        wildcardExtensionIs=".html", bookTxtIsSpecial=False,
        infileAsStdin=False, stdinIsBook=False,
        ignoreTransclusions=False, justRaw=False):
        """Take a single inputfile and produce a merged output file, then
        dump the output to stdout.

        Args:
            infilePath: the input file path, relative to self.__dataDir
            expectedFilePath: the expected file path, relative to
                self.__dataDir. Defaults to None.
            expectingStderr: if True then the stderr stream should have
                some content.
            wildcardExtensionIs: the extension to substitute if include
                file extension is a wildcardExtensionIs
            bookTxtIsSpecial: whether to treat 'book.txt' as a Leanpub index
                file.
            infileAsStdin: the CUT should access the infile via STDIN
            stdinIsBook: whether STDIN is treated as an index file
            ignoreTransclusions: whether MultiMarkdown transclusion
                specifications should be left untouched
            justRaw: whether to only process raw include specifications

        """

        infilePath = os.path.join(self.__dataDir, infilePath)
        if None != expectedfilePath:
            expectedfilePath = os.path.join(self.__dataDir, expectedfilePath)
            expectedSize = os.stat(expectedfilePath).st_size
        outfilePath = os.path.join(self.tempDirPath.name, "result.mmd")
        errfilePath = os.path.join(self.tempDirPath.name, "result.err")
        if infileAsStdin:
            with io.open(outfilePath, "w") as outfile, \
                io.open(errfilePath, "w") as errfile, \
                io.open(infilePath, "r") as infile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdin=infile, stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcardExtensionIs, bookTxtIsSpecial, stdinIsBook,
                    ignoreTransclusions, justRaw)
                infileNode = Node(
                    os.path.dirname(os.path.abspath(infilePath)))
                cut.merge(infileNode, sys.stdout)
        else:
            with io.open(outfilePath, "w") as outfile, \
                io.open(errfilePath, "w") as errfile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcardExtensionIs, bookTxtIsSpecial, stdinIsBook,
                    ignoreTransclusions, justRaw)
                infileNode = Node(filePath=infilePath)
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
            infileNode = Node(filePath=infilePath)
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

    def testSingleIncludeFencedTransclusionLong(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence (where
        the fence is 6 ticks, not 3)

        """

        self._mergeTest("t-c-long.mmd", "expected-t-c-long.mmd")

    def testSingleIncludeFencedTransclusionTildes(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence (where
        the fence is tildes (~))

        """

        self._mergeTest("t-c2.mmd", "expected-t-c2.mmd")

    def testSingleIncludeFencedTransclusionIgnored(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence,
        but with the transclusions ignored.

        """

        self._mergeTest("t-c.mmd", "t-c.mmd", ignoreTransclusions=True)

    def testSingleIncludeFencedTransclusionIgnoredLong(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence,
        but with the transclusions ignored. The fence is 6 ticks not 3.

        """

        self._mergeTest(
            "t-c-long.mmd", "t-c-long.mmd", ignoreTransclusions=True)

    def testSingleIncludeFencedTransclusionIgnoredTildes(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence,
        but with the transclusions ignored. The fence is tildes not ticks.

        """

        self._mergeTest("t-c2.mmd", "t-c2.mmd", ignoreTransclusions=True)

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

    def testSingleIncludeNamedFencedTransclusionLong(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside a named code fence. fence
        is longer than three backticks.

        """

        self._mergeTest("t-c-long-named.mmd", "expected-t-c-long-named.mmd")

    def testSingleIncludeNamedFencedTransclusionTildes(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside a named code fence. fence
        is tildes.

        """

        self._mergeTest("t-c2-named.mmd", "expected-t-c2-named.mmd")

    def testSingleIncludeRawDefault(self):
        """Test MarkdownMerge.merge().

        A file with one raw include specification. That spec should be
        ignored by default.

        """

        self._mergeTest("r-a.mmd", "expected-r-a.mmd")

    def testSingleIncludeRawJustRaw(self):
        """Test MarkdownMerge.merge().

        A file with one raw include specification. Because --just-raw
        is specified, that spec should be processed.

        """

        self._mergeTest("r-a.mmd", "expected-r-aa.mmd", justRaw=True)

    def testSingleIncludeTransclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion.

        """

        self._mergeTest("t-a.mmd", "expected-t-a.mmd")

    def testSingleIncludeTransclusionIgnored(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion, but with the transclusion
        ignored.

        """

        self._mergeTest("t-a.mmd", "t-a.mmd", ignoreTransclusions=True)

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

    def testChildToSelfCycle(self):
        """Test MarkdownMerge.merge().

        A parent includes itself.

        """
        with self.assertRaises(AssertionError):
            self._mergeTest("cycle-i.mmd")

    def testBookTextIsNotSpecial(self):
        """Test MarkdownMerge.merge().

        A Leanpub index file called 'book.txt' but without the flag
        indicating that it is special.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(self.__dataDir, "lp-book.txt")
        tgtPath = os.path.join(inputdirPath, "book.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "book.txt")
        self._mergeTest(absInfilePath, "expected-unmerged-book.txt")

    def testBookTextIsSpecial(self):
        """Test MarkdownMerge.merge().

        A file with the special name 'book.txt' is recognized
        as a leanpub index and processed as such.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(self.__dataDir, "lp-book.txt")
        tgtPath = os.path.join(inputdirPath, "book.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "book.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd", bookTxtIsSpecial=True)

    def testBookTextMissingFile(self):
        """Test MarkdownMerge.merge().

        A leanpub index contains a non-extant file. Show that is
        the file is ignored but a warning is issued to stderr.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(self.__dataDir, "lp-book-bad1.txt")
        tgtPath = os.path.join(inputdirPath, "book.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "book.txt")
        self._mergeTest(
            absInfilePath, "expected-book-bad1.mmd",
            bookTxtIsSpecial=True, expectingStderr=True)

    def testLeanpubIndex(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a leanpub index because the first line
        is 'frontmatter:'; it is processed as a leanpub index.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(self.__dataDir, "lp-index.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd")

    def testLeanpubIndexWithBlanksAndComments(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a leanpub index because the first line
        is 'frontmatter:'; it is processed as a leanpub index. All blanks
        and comments are ignored.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "lp-index-with-spaces.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd")

    def testLeanpubIndexWithLeadingBlanksAndComments(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a leanpub index because the first non-blank,
        non-comment line is 'frontmatter:'; it is processed as a leanpub
        index. All blanks and comments are ignored.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "lp-index-with-leading-spaces.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd")

    def testLeanpubIndexMissingFile(self):
        """Test MarkdownMerge.merge().

        A leanpub index contains a non-extant file. Show that is
        the file is ignored but a warning is issued to stderr.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(self.__dataDir, "lp-index-bad1.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book-bad1.mmd",
            expectingStderr=True)

    def testMmdIndex(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(self.__dataDir, "mmd-index.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd")

    def testMmdIndexVariation(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#  merge:'; it is processed as a mmd_merge index.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "mmd-index-variation.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd")

    def testMmdIndexWithBlanksAndComments(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because of a leading
        '#merge' comment; but the file contains leanpub meta tags and
        other comments and blanks. It is processed as a mmd_merge index.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "mmd-index-with-comments-and-blanks.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book.mmd")

    def testMmdIndexIndentedWithTabs(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index. The file contains
        indentation, so the merged file has headings levels that match
        the indentation.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "mmd-index-indentation-tabs.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book-indentation.mmd")

    def testMmdIndexIndentedWithExactSpaces(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index. The file contains
        indentation, so the merged file has headings levels that match
        the indentation. The indentation is spaces rather than tabs.

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "mmd-index-indentation-exact-spaces.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book-indentation.mmd")

    def testMmdIndexIndentedWithInexactSpaces(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index. The file contains
        indentation, so the merged file has headings levels that match
        the indentation. The indentation is spaces, and not in even multiples
        of 4 (four).

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "mmd-index-indentation-inexact-spaces.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book-indentation.mmd")

    def testMultiIncludesWith2Files(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 2 files.

        """

        self._mergeTest("d-root2.mmd", "expected-d-root2.mmd")

    def testMultiIncludesWith3Files(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 3 files.

        """

        self._mergeTest("d-root3.mmd", "expected-d-root3.mmd")

    def testMultiIncludesWith4Files(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 4 files.

        """

        self._mergeTest("d-root4.mmd", "expected-d-root4.mmd")

    def testStdinNoIncludes(self):
        """Test MarkdownMerge.merge().

        stdin with no includes should produce an identical file.

        """

        self._mergeTest("aa.mmd", "aa.mmd", infileAsStdin=True)

    def testStdinSingleIncludeFencedTransclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence.

        """

        self._mergeTest("t-c.mmd", "expected-t-c.mmd", infileAsStdin=True)

    def testStdinMmdIndexIndentedWithInexactSpaces(self):
        """Test MarkdownMerge.merge().

        STDIN is treated as in index because of the '--book' argument.
        The file contains indentation, so the merged file has headings levels
        that match the indentation. The indentation is spaces, and not in
        even multiples of 4 (four).

        """

        # create the temp directory
        inputdirPath = os.path.join(self.tempDirPath.name, "Inputs")
        os.makedirs(inputdirPath)

        # copy the index file to a temp directory
        absTestfilePath = os.path.join(
            self.__dataDir, "mmd-index-indentation-inexact-spaces.txt")
        tgtPath = os.path.join(inputdirPath, "merge-this.txt")
        shutil.copy(absTestfilePath, tgtPath)

        # copy the input files to a temp directory
        testfilePaths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfilePath in testfilePaths:
            absTestfilePath = os.path.join(self.__dataDir, testfilePath)
            shutil.copy(absTestfilePath, inputdirPath)

        # run the test
        absInfilePath = os.path.join(inputdirPath, "merge-this.txt")
        self._mergeTest(
            absInfilePath, "expected-book-indentation.mmd",
            infileAsStdin=True, stdinIsBook=True)

    def testWildcardIncludeLeanpubDefault(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html,
        by default.

        """

        self._mergeTest(
            "w.mmd", "expected-w-html.mmd")

    def testWildcardIncludeLeanpubHtml(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html.

        """

        self._mergeTest(
            "w.mmd", "expected-w-html.mmd", wildcardExtensionIs=".html")

    def testWildcardIncludeLeanpubLatex(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is latex.

        """

        self._mergeTest(
            "w.mmd", "expected-w-latex.mmd", wildcardExtensionIs=".tex")

    def testWildcardIncludeLeanpubLyx(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is lyx.

        """

        self._mergeTest(
            "w.mmd", "expected-w-lyx.mmd", wildcardExtensionIs=".lyx")

    def testWildcardIncludeLeanpubOdf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is odf.

        """

        self._mergeTest(
            "w.mmd", "expected-w-odf.mmd", wildcardExtensionIs=".odf")

    def testWildcardIncludeLeanpubOpml(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is opml.

        """

        self._mergeTest(
            "w.mmd", "expected-w-opml.mmd", wildcardExtensionIs=".opml")

    def testWildcardIncludeLeanpubRtf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is rtf.

        """

        self._mergeTest(
            "w.mmd", "expected-w-rtf.mmd", wildcardExtensionIs=".rtf")

    def testWildcardTransclusionDefault(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html,
        by default.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-html.mmd")

    def testWildcardTransclusionHtml(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-html.mmd", wildcardExtensionIs=".html")

    def testWildcardTransclusionLatex(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is latex.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-latex.mmd", wildcardExtensionIs=".tex")

    def testWildcardTransclusionLyx(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is lyx.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-lyx.mmd", wildcardExtensionIs=".lyx")

    def testWildcardTransclusionOdf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is odf.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-odf.mmd", wildcardExtensionIs=".odf")

    def testWildcardTransclusionOpml(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is opml.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-opml.mmd", wildcardExtensionIs=".opml")

    def testWildcardTransclusionRtf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is rtf.

        """

        self._mergeTest(
            "t-w.mmd", "expected-w-rtf.mmd", wildcardExtensionIs=".rtf")

    def testUnicodeSingleIncludeMarked(self):
        """Test MarkdownMerge.merge().

        A unicode (non-ascii) file with one Marked include.

        """

        self._mergeTest("u.mmd", "expected-u.mmd")

    def testUnicodeFirstLineSingleIncludeMarked(self):
        """Test MarkdownMerge.merge().

        A unicode (non-ascii) file with one Marked include.

        """

        self._mergeTest("u2.mmd", "expected-u2.mmd")

# eof