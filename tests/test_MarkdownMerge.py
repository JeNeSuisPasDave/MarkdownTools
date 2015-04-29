# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""Unit tests for the MarkdownMerge module, MarkdownMerge class."""

import unittest
import os
import os.path
import sys
import io
import shutil
from mdmerge.markdownMerge import MarkdownMerge
from mdmerge.node import Node

import pprint


class MarkdownMergeTests(unittest.TestCase):

    """Unit tests for the markdownMerge.py module."""

    class RedirectStdStreams:

        """A context manager for standard streams.

        A context manager that can temporarily redirect the standard
        streams.

        """

        def __init__(self, stdin=None, stdout=None, stderr=None):
            """Constructor."""
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
        """Constructor."""
        self.devnull = open(os.devnull, "w")
        super().__init__(*args)
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

    def _merge_test(
            self,
            infile_path, expectedfile_path=None, expecting_stderr=False,
            wildcard_extension_is=".html", book_txt_is_special=False,
            infile_as_stdin=False, stdin_is_book=False,
            ignore_transclusions=False, just_raw=False):
        """Merge input file and check output against expected output.

        Take a single inputfile and produce a merged output file, then
        check the results against a file containing the expected content.

        Args:
            infile_path: the input file path, relative to self.__dataDir
            expectedfile_path: the expected file path, relative to
                self.__dataDir. Defaults to None.
            expecting_stderr: if True then the stderr stream should have
                some content.
            wildcard_extension_is: the extension to substitute if include
                file extension is a wildcard_extension_is
            book_txt_is_special: whether to treat 'book.txt' as a Leanpub index
                file.
            infile_as_stdin: the CUT should access the infile via STDIN
            stdin_is_book: whether STDIN is treated as an index file
            ignore_transclusions: whether MultiMarkdown transclusion
                specifications should be left untouched
            just_raw: whether to only process raw include specifications

        """
        # TODO: take cut constructor arguments as a dictionary argument

        infile_path = os.path.join(self.__dataDir, infile_path)
        if None != expectedfile_path:
            expectedfile_path = os.path.join(self.__dataDir, expectedfile_path)
            expected_size = os.stat(expectedfile_path).st_size
        outfile_path = os.path.join(self.temp_dir_path.name, "result.mmd")
        errfile_path = os.path.join(self.temp_dir_path.name, "result.err")
        if infile_as_stdin:
            with io.open(outfile_path, "w") as outfile, \
                io.open(errfile_path, "w") as errfile, \
                io.open(infile_path, "r") as infile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdin=infile, stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcard_extension_is, book_txt_is_special, stdin_is_book,
                    ignore_transclusions, just_raw)
                infile_node = Node(os.path.dirname(infile_path))
                cut.merge(infile_node, sys.stdout)
        else:
            with io.open(outfile_path, "w") as outfile, \
                io.open(errfile_path, "w") as errfile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcard_extension_is, book_txt_is_special, stdin_is_book,
                    ignore_transclusions, just_raw)
                infile_node = Node(file_path=infile_path)
                cut.merge(infile_node, sys.stdout)
        if expecting_stderr:
            self.assertGreater(os.stat(errfile_path).st_size, 0)
        else:
            self.assertEqual(0, os.stat(errfile_path).st_size)
        if None != expectedfile_path:
            self.assertEqual(expected_size, os.stat(outfile_path).st_size)
            self.assertTrue(self._are_files_identical(
                expectedfile_path, outfile_path))

    def _merge_try(
            self,
            infile_path, expectedfile_path=None, expecting_stderr=False,
            wildcard_extension_is=".html", book_txt_is_special=False,
            infile_as_stdin=False, stdin_is_book=False,
            ignore_transclusions=False, just_raw=False):
        """Merge inputfile and dump output to stdout.

        Take a single inputfile and produce a merged output file, then
        dump the output to stdout.

        Args:
            infile_path: the input file path, relative to self.__dataDir
            expectedfile_path: the expected file path, relative to
                self.__dataDir. Defaults to None.
            expecting_stderr: if True then the stderr stream should have
                some content.
            wildcard_extension_is: the extension to substitute if include
                file extension is a wildcard_extension_is
            book_txt_is_special: whether to treat 'book.txt' as a Leanpub index
                file.
            infile_as_stdin: the CUT should access the infile via STDIN
            stdin_is_book: whether STDIN is treated as an index file
            ignore_transclusions: whether MultiMarkdown transclusion
                specifications should be left untouched
            just_raw: whether to only process raw include specifications

        """
        infile_path = os.path.join(self.__dataDir, infile_path)
        outfile_path = os.path.join(self.temp_dir_path.name, "result.mmd")
        errfile_path = os.path.join(self.temp_dir_path.name, "result.err")
        if infile_as_stdin:
            with io.open(outfile_path, "w") as outfile, \
                io.open(errfile_path, "w") as errfile, \
                io.open(infile_path, "r") as infile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdin=infile, stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcard_extension_is, book_txt_is_special, stdin_is_book,
                    ignore_transclusions, just_raw)
                infile_node = Node(
                    os.path.dirname(os.path.abspath(infile_path)))
                cut.merge(infile_node, sys.stdout)
        else:
            with io.open(outfile_path, "w") as outfile, \
                io.open(errfile_path, "w") as errfile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdout=outfile, stderr=errfile):
                cut = MarkdownMerge(
                    wildcard_extension_is, book_txt_is_special, stdin_is_book,
                    ignore_transclusions, just_raw)
                infile_node = Node(file_path=infile_path)
                cut.merge(infile_node, sys.stdout)

        with io.open(outfile_path, "r") as outfile:
            for line in outfile:
                print(line, end='')
        if 0 != os.stat(errfile_path).st_size:
            with io.open(errfile_path, "r") as errfile:
                for line in errfile:
                    print(line, end='')

    def _merge_try_pass_err(
            self,
            infile_path, expectedfile_path=None, expecting_stderr=False,
            wildcard_extension_is=".html", book_txt_is_special=False,
            infile_as_stdin=False, stdin_is_book=False,
            ignore_transclusions=False, just_raw=False):
        """Merge inputfile and dump output to stdout.

        Take a single inputfile and produce a merged output file, then
        dump the output to stdout.

        Args:
            infile_path: the input file path, relative to self.__dataDir
            expectedfile_path: the expected file path, relative to
                self.__dataDir. Defaults to None.
            expecting_stderr: if True then the stderr stream should have
                some content.
            wildcard_extension_is: the extension to substitute if include
                file extension is a wildcard_extension_is
            book_txt_is_special: whether to treat 'book.txt' as a Leanpub index
                file.
            infile_as_stdin: the CUT should access the infile via STDIN
            stdin_is_book: whether STDIN is treated as an index file
            ignore_transclusions: whether MultiMarkdown transclusion
                specifications should be left untouched
            just_raw: whether to only process raw include specifications

        """
        infile_path = os.path.join(self.__dataDir, infile_path)
        outfile_path = os.path.join(self.temp_dir_path.name, "result.mmd")
        if infile_as_stdin:
            with io.open(outfile_path, "w") as outfile, \
                io.open(infile_path, "r") as infile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdin=infile, stdout=outfile, stderr=None):
                cut = MarkdownMerge(
                    wildcard_extension_is, book_txt_is_special, stdin_is_book,
                    ignore_transclusions, just_raw)
                infile_node = Node(
                    os.path.dirname(os.path.abspath(infile_path)))
                cut.merge(infile_node, sys.stdout)
        else:
            with io.open(outfile_path, "w") as outfile, \
                MarkdownMergeTests.RedirectStdStreams(
                    stdout=outfile, stderr=None):
                cut = MarkdownMerge(
                    wildcard_extension_is, book_txt_is_special, stdin_is_book,
                    ignore_transclusions, just_raw)
                infile_node = Node(file_path=infile_path)
                cut.merge(infile_node, sys.stdout)

        with io.open(outfile_path, "r") as outfile:
            for line in outfile:
                print(line, end='')

    def _side_effect_expand_user(self, path):
        if not path.startswith("~"):
            return path
        path = path.replace("~", self.temp_dir_path.name)
        return path

    # -------------------------------------------------------------------------+
    # setup, teardown, noop
    # -------------------------------------------------------------------------+

    def setUp(self):
        """Create data used by the test cases."""
        import tempfile

        self.temp_dir_path = tempfile.TemporaryDirectory()
        return

    def tearDown(self):
        """Cleanup data used by the test cases."""
        self.temp_dir_path.cleanup()
        self.temp_dir_path = None

    def test_no_op(self):
        """Excercise tearDown and setUp methods.

        This test does nothing itself. It is useful to test the tearDown()
        and setUp() methods in isolation (without side effects).

        """
        return

    # -------------------------------------------------------------------------+
    # tests for MarkdownMerge.merge()
    # -------------------------------------------------------------------------+

    def test_empty_input(self):
        """Test MarkdownMerge.merge().

        A zero length file should produce a zero length output.

        """
        infile_path = os.path.join(self.__dataDir, "empty.mmd")
        outfile_path = os.path.join(self.temp_dir_path.name, "result.mmd")
        errfile_path = os.path.join(self.temp_dir_path.name, "result.err")
        with io.open(outfile_path, "w") as outfile, \
            io.open(errfile_path, "w") as errfile, \
            MarkdownMergeTests.RedirectStdStreams(
                stdout=outfile, stderr=errfile):
            cut = MarkdownMerge(".html")
            infile_node = Node(file_path=infile_path)
            cut.merge(infile_node, sys.stdout)
        self.assertEqual(0, os.stat(outfile_path).st_size)
        self.assertEqual(0, os.stat(errfile_path).st_size)

    def test_nested_include_marked_complex_metadata(self):
        """Test MarkdownMerge.merge().

        A file with nested Marked includes and multiple metadata lines.

        """
        self._merge_test("m.mmd", "expected-m.mmd")

    def test_nested_include_marked_complex_yaml_metadata(self):
        """Test MarkdownMerge.merge().

        A file with nested Marked includes and multiple metadata lines.

        """
        self._merge_test("m-y.mmd", "expected-m-y.mmd")

    def test_no_includes(self):
        """Test MarkdownMerge.merge().

        A file with no includes should produce an identical file.

        """
        self._merge_test("aa.mmd", "aa.mmd")

    def test_single_include_fenced_transclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence.

        """
        self._merge_test("t-c.mmd", "expected-t-c.mmd")

    def test_single_include_fenced_transclusion_long(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence (where
        the fence is 6 ticks, not 3)

        """
        self._merge_test("t-c-long.mmd", "expected-t-c-long.mmd")

    def test_single_include_fenced_transclusion_tildes(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence (where
        the fence is tildes (~))

        """
        self._merge_test("t-c2.mmd", "expected-t-c2.mmd")

    def test_single_include_fenced_transclusion_ignored(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence,
        but with the transclusions ignored.

        """
        self._merge_test("t-c.mmd", "t-c.mmd", ignore_transclusions=True)

    def test_single_include_fenced_transclusion_ignored_long(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence,
        but with the transclusions ignored. The fence is 6 ticks not 3.

        """
        self._merge_test(
            "t-c-long.mmd", "t-c-long.mmd", ignore_transclusions=True)

    def test_single_include_fenced_transclusion_ignored_tildes(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence,
        but with the transclusions ignored. The fence is tildes not ticks.

        """
        self._merge_test("t-c2.mmd", "t-c2.mmd", ignore_transclusions=True)

    def test_single_include_leanpub_code(self):
        """Test MarkdownMerge.merge().

        A file with one leanpub include specification.

        """
        self._merge_test("lp-a.mmd", "expected-lp-a.mmd")

    def test_single_include_leanpub_titled_code(self):
        """Test MarkdownMerge.merge().

        A file with one titled leanpub include specification.

        """
        self._merge_test("lpt-a.mmd", "expected-lpt-a.mmd")

    def test_single_include_marked(self):
        """Test MarkdownMerge.merge().

        A file with one Marked include.

        """
        self._merge_test("a.mmd", "expected-a.mmd")

    def test_single_include_named_fenced_transclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside a named code fence.

        """
        self._merge_test("t-c-named.mmd", "expected-t-c-named.mmd")

    def test_single_include_named_fenced_transclusion_long(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside a named code fence. fence
        is longer than three backticks.

        """
        self._merge_test("t-c-long-named.mmd", "expected-t-c-long-named.mmd")

    def test_single_include_named_fenced_transclusion_tildes(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside a named code fence. fence
        is tildes.

        """
        self._merge_test("t-c2-named.mmd", "expected-t-c2-named.mmd")

    def test_single_include_raw_default(self):
        """Test MarkdownMerge.merge().

        A file with one raw include specification. That spec should be
        ignored by default.

        """
        self._merge_test("r-a.mmd", "expected-r-a.mmd")

    def test_single_include_raw_just_raw(self):
        """Test MarkdownMerge.merge().

        A file with one raw include specification. Because --just-raw
        is specified, that spec should be processed.

        """
        self._merge_test("r-a.mmd", "expected-r-aa.mmd", just_raw=True)

    def test_single_include_transclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion.

        """
        self._merge_test("t-a.mmd", "expected-t-a.mmd")

    def test_single_include_transclusion_ignored(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion, but with the transclusion
        ignored.

        """
        self._merge_test("t-a.mmd", "t-a.mmd", ignore_transclusions=True)

    def test_child_to_parent_cycle(self):
        """Test MarkdownMerge.merge().

        A child include file that includes its parent.

        """
        with self.assertRaises(AssertionError):
            self._merge_test("cycle-a.mmd")

    def test_child_to_ancestor_cycle(self):
        """Test MarkdownMerge.merge().

        A deep child include file that includes an ancestor
        a couple parents away.

        """
        with self.assertRaises(AssertionError):
            self._merge_test("cycle-b.mmd")

    def test_child_to_self_cycle(self):
        """Test MarkdownMerge.merge().

        A parent includes itself.

        """
        with self.assertRaises(AssertionError):
            self._merge_test("cycle-i.mmd")

    def test_book_text_is_not_special(self):
        """Test MarkdownMerge.merge().

        A Leanpub index file called 'book.txt' but without the flag
        indicating that it is special.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "lp-book.txt")
        tgt_path = os.path.join(inputdir_path, "book.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "book.txt")
        self._merge_test(abs_infile_path, "expected-unmerged-book.txt")

    def test_book_text_is_special(self):
        """Test MarkdownMerge.merge().

        A file with the special name 'book.txt' is recognized
        as a leanpub index and processed as such.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "lp-book.txt")
        tgt_path = os.path.join(inputdir_path, "book.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "book.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd", book_txt_is_special=True)

    def test_book_text_missing_file(self):
        """Test MarkdownMerge.merge().

        A leanpub index contains a non-extant file. Show that is
        the file is ignored but a warning is issued to stderr.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "lp-book-bad1.txt")
        tgt_path = os.path.join(inputdir_path, "book.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "book.txt")
        self._merge_test(
            abs_infile_path, "expected-book-bad1.mmd",
            book_txt_is_special=True, expecting_stderr=True)

    def test_leanpub_index(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a leanpub index because the first line
        is 'frontmatter:'; it is processed as a leanpub index.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "lp-index.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd")

    def test_leanpub_index_with_blanks_and_comments(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a leanpub index because the first line
        is 'frontmatter:'; it is processed as a leanpub index. All blanks
        and comments are ignored.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "lp-index-with-spaces.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd")

    def test_leanpub_index_with_leading_blanks_and_comments(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a leanpub index because the first non-blank,
        non-comment line is 'frontmatter:'; it is processed as a leanpub
        index. All blanks and comments are ignored.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "lp-index-with-leading-spaces.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd")

    def test_leanpub_index_missing_file(self):
        """Test MarkdownMerge.merge().

        A leanpub index contains a non-extant file. Show that is
        the file is ignored but a warning is issued to stderr.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "lp-index-bad1.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book-bad1.mmd",
            expecting_stderr=True)

    def test_mmd_index(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(self.__dataDir, "mmd-index.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd")

    def test_mmd_index_variation(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#  merge:'; it is processed as a mmd_merge index.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "mmd-index-variation.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd")

    def test_mmd_index_with_metadata(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
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
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book-m.mmd")

    def test_mmd_index_with_blanks_and_comments(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because of a leading
        '#merge' comment; but the file contains leanpub meta tags and
        other comments and blanks. It is processed as a mmd_merge index.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "mmd-index-with-comments-and-blanks.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book.mmd")

    def test_mmd_index_indented_with_tabs(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index. The file contains
        indentation, so the merged file has headings levels that match
        the indentation.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "mmd-index-indentation-tabs.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book-indentation.mmd")

    def test_mmd_index_indented_with_exact_spaces(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index. The file contains
        indentation, so the merged file has headings levels that match
        the indentation. The indentation is spaces rather than tabs.

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "mmd-index-indentation-exact-spaces.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book-indentation.mmd")

    def test_mmd_index_indented_with_inexact_spaces(self):
        """Test MarkdownMerge.merge().

        A file is recognized as a multimarkdown index because the first line
        is '#merge:'; it is processed as a mmd_merge index. The file contains
        indentation, so the merged file has headings levels that match
        the indentation. The indentation is spaces, and not in even multiples
        of 4 (four).

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "mmd-index-indentation-inexact-spaces.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book-indentation.mmd")

    def test_multi_includes_with_2_files(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 2 files.

        """
        self._merge_test("d-root2.mmd", "expected-d-root2.mmd")

    def test_multi_includes_with_3_files(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 3 files.

        """
        self._merge_test("d-root3.mmd", "expected-d-root3.mmd")

    def test_multi_includes_with_3_files_last_at_end_of_root(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 3 files, with the last include
        being the last line of the file.

        """
        self._merge_test("d-root3a.mmd", "expected-d-root3a.mmd")

    def test_multi_includes_with_4_files(self):
        """Test MarkdownMerge.merge().

        This is a root document that includes 4 files.

        """
        self._merge_test("d-root4.mmd", "expected-d-root4.mmd")

    def test_stdin_no_includes(self):
        """Test MarkdownMerge.merge().

        stdin with no includes should produce an identical file.

        """
        self._merge_test("aa.mmd", "aa.mmd", infile_as_stdin=True)

    def test_stdin_single_include_fenced_transclusion(self):
        """Test MarkdownMerge.merge().

        A file with one MMD transclusion inside an unnamed code fence.

        """
        self._merge_test("t-c.mmd", "expected-t-c.mmd", infile_as_stdin=True)

    def test_stdin_mmd_index_indented_with_inexact_spaces(self):
        """Test MarkdownMerge.merge().

        STDIN is treated as in index because of the '--book' argument.
        The file contains indentation, so the merged file has headings levels
        that match the indentation. The indentation is spaces, and not in
        even multiples of 4 (four).

        """
        # create the temp directory
        inputdir_path = os.path.join(self.temp_dir_path.name, "Inputs")
        os.makedirs(inputdir_path)

        # copy the index file to a temp directory
        abs_testfile_path = os.path.join(
            self.__dataDir, "mmd-index-indentation-inexact-spaces.txt")
        tgt_path = os.path.join(inputdir_path, "merge-this.txt")
        shutil.copy(abs_testfile_path, tgt_path)

        # copy the input files to a temp directory
        testfile_paths = ([
            "book-ch1.mmd", "book-ch2.mmd", "book-ch3.mmd",
            "book-end.mmd", "book-front.mmd", "book-index.mmd",
            "book-toc.mmd"])
        for testfile_path in testfile_paths:
            abs_testfile_path = os.path.join(self.__dataDir, testfile_path)
            shutil.copy(abs_testfile_path, inputdir_path)

        # run the test
        abs_infile_path = os.path.join(inputdir_path, "merge-this.txt")
        self._merge_test(
            abs_infile_path, "expected-book-indentation.mmd",
            infile_as_stdin=True, stdin_is_book=True)

    def test_wildcard_include_leanpub_default(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html,
        by default.

        """
        self._merge_test(
            "w.mmd", "expected-w-html.mmd")

    def test_wildcard_include_leanpub_html(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html.

        """
        self._merge_test(
            "w.mmd", "expected-w-html.mmd", wildcard_extension_is=".html")

    def test_wildcard_include_leanpub_latex(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is latex.

        """
        self._merge_test(
            "w.mmd", "expected-w-latex.mmd", wildcard_extension_is=".tex")

    def test_wildcard_include_leanpub_lyx(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is lyx.

        """
        self._merge_test(
            "w.mmd", "expected-w-lyx.mmd", wildcard_extension_is=".lyx")

    def test_wildcard_include_leanpub_odf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is odf.

        """
        self._merge_test(
            "w.mmd", "expected-w-odf.mmd", wildcard_extension_is=".odf")

    def test_wildcard_include_leanpub_opml(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is opml.

        """
        self._merge_test(
            "w.mmd", "expected-w-opml.mmd", wildcard_extension_is=".opml")

    def test_wildcard_include_leanpub_rtf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is rtf.

        """
        self._merge_test(
            "w.mmd", "expected-w-rtf.mmd", wildcard_extension_is=".rtf")

    def test_wildcard_transclusion_default(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html,
        by default.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-html.mmd")

    def test_wildcard_transclusion_html(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is html.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-html.mmd", wildcard_extension_is=".html")

    def test_wildcard_transclusion_latex(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is latex.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-latex.mmd", wildcard_extension_is=".tex")

    def test_wildcard_transclusion_lyx(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is lyx.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-lyx.mmd", wildcard_extension_is=".lyx")

    def test_wildcard_transclusion_odf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is odf.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-odf.mmd", wildcard_extension_is=".odf")

    def test_wildcard_transclusion_opml(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is opml.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-opml.mmd", wildcard_extension_is=".opml")

    def test_wildcard_transclusion_rtf(self):
        """Test MarkdownMerge.merge().

        One of the includes has a wildcard extension. Export target is rtf.

        """
        self._merge_test(
            "t-w.mmd", "expected-w-rtf.mmd", wildcard_extension_is=".rtf")

    def test_unicode_single_include_marked(self):
        """Test MarkdownMerge.merge().

        A unicode (non-ascii) file with one Marked include.

        """
        self._merge_test("u.mmd", "expected-u.mmd")

    def test_unicode_first_line_single_include_marked(self):
        """Test MarkdownMerge.merge().

        A unicode (non-ascii) file with one Marked include.

        """
        self._merge_test("u2.mmd", "expected-u2.mmd")

# eof
