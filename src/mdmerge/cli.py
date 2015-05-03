# Copyright 2015 Dave Hein
#
# This file is part of MarkdownTools
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Module of classes to handle command line input."""

from __future__ import print_function, with_statement, generators, \
    unicode_literals
import argparse
import os
import os.path
import stat
import sys
import io

from .node import Node
from .markdownMerge import MarkdownMerge


class CLI:

    """Handle the command line interface.

    Handle the command line interface, invoking MarkdownMerge as
    needed.

    """

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

    # class attributes
    #
    __STDIN_FILENAME = '-'

    def __init__(self, stdin=None, stdout=None, stderr=None):
        """Constructor."""
        self.__stdin_redirected = False
        if stdin is not None:
            self.__stdin = stdin
            self.__stdin_redirected = True
        else:
            self.__stdin = sys.stdin
        self.__stdout_redirected = False
        if stdout is not None:
            self.__stdout = stdout
            self.__stdout_redirected = True
        else:
            self.__stdout = sys.stdout
        self.__stderr_redirected = False
        if stderr is not None:
            self.__stderr = stderr
            self.__stderr_redirected = True
        else:
            self.__stderr = sys.stderr

        self.__abandon_cli = False
        self.__use_stdin = False
        self.__pos_stdin = 0
        self.__use_stdout = True
        self.__out_filepath = None
        self.__out_file = None
        self.__input_filepaths = []
        self.__book_txt_is_special = False
        self.__wildcard_extension_is = None
        self.__stdin_is_book = False
        self.__ignore_transclusions = False
        self.__just_raw = False

        # main command
        #
        self.parser = argparse.ArgumentParser(
            description=(
                "Concatenate and include multiple markdown"
                "files into a single file"),
            prog='mdmerge')
        self.parser.add_argument(
            '--version', dest='showVersion', action='store_true',
            default=False, help="show the software version")
        self.parser.add_argument(
            "--export-target", dest='exportTarget', action='store',
            choices=['html', 'latex', 'lyx', 'opml', 'rtf', 'odf'],
            default='html',
            help="Guide include file wildcard substitution")
        self.parser.add_argument(
            "--ignore-transclusions", dest='ignoreTransclusions',
            action='store_true',
            default=False,
            help="MultiMarkdown transclusion specifications are untouched")
        self.parser.add_argument(
            "--just-raw", dest='justRaw', action='store_true',
            default=False,
            help="Process only raw include specifications")
        self.parser.add_argument(
            "--leanpub", dest='leanPub', action='store_true',
            default=False,
            help="Any file called 'book.txt' will be treated as an index file")
        self.parser.add_argument(
            "--book", dest='forceBook', action='store_true',
            default=False,
            help="Treat STDIN as an index file")
        self.parser.add_argument(
            '-o', '--outfile', dest='outFile', action='store',
            help="Specify the path to the output file")
        self.parser.add_argument(
            dest='inFiles', metavar='inFile', nargs='*', type=str,
            help="""One or more files to merge, or just '-' for STDIN. If
            multiple files are provide then they will be treated as if they
            were listed in an index file.""")

    def _is_sequence_not_string(self, obj):
        """Determine whether the object is a string."""
        return (
            not hasattr(obj, "strip") and
            hasattr(obj, "__getitem__") or
            hasattr(obj, "__iter__"))

    def _is_sequence_of_chars(self, obj):
        """Determine whether the object is a char sequence."""
        if not self._is_sequence_not_string(obj):
            return False
        if (0 == len(obj)):
            return False
        for c in obj:
            if 1 != len(c):
                return False
        return True

    def _show_version(self):
        """Show the version only."""
        import mdmerge

        print(
            "mdmerge version {0}".format(mdmerge.__version__),
            file=self.__stdout)
        print(
            "{0}. Licensed under {1}.".format(
                mdmerge.__copyright__, mdmerge.__license__),
            file=self.__stdout)

    def _stdin_is_tty(self):
        """Detect whether the stdin is mapped to a terminal console.

        I found this technique in the answer by thg435 here:
        http://stackoverflow.com/questions/13442574/how-do-i-determine-if-sys-stdin-is-redirected-from-a-file-vs-piped-from-another

        """
        mode = os.fstat(0).st_mode
        if ((not stat.S_ISFIFO(mode))
                and (not stat.S_ISREG(mode))):
            # not piped (not FIFO) and not redirected (not REG), so assume
            # terminal input
            #
            return True
        else:
            # is either piped or redirected, so assume not terminal input
            #
            return False

    def _validate_args(self):
        """Validate and capture the command line arguments.

        Validate the command line arguments and set fields based on those
        arguments.

        Raises:
            IOError: there was a problem validating the files specified on
            the command line.

        """
        # if '--version' specified, ignore remainder of command line
        #
        if self.args.showVersion:
            if 'subcmd' in dir(self.args):
                self.args.subcmd = None
            return
        # Check the output file
        #
        if self.args.outFile is not None:
            self.__use_stdout = False
            self.__out_filepath = self._validate_output_filepath(
                self.args.outFile)
        # Check the input files
        #
        if 0 == len(self.args.inFiles):
            self.parser.error(
                "You must specify at least one input. " +
                "Either '-' for stdin, or a list of files separated " +
                "by whitespace.")
        # if there was just one input file provided, then argparse
        # may have interpreted that as a list of characters rather than
        # as a string. So we need to convert it back to a list containing
        # a single string element.
        #
        if (self.args.inFiles
                and self._is_sequence_of_chars(self.args.inFiles)):
            self.args.inFiles = [''.join(self.args.inFiles)]
        # Now validate the input file paths (or the '-' stdin designator)
        #
        for fp in self.args.inFiles:
            ffp = None
            if ((1 == len(self.args.inFiles))
                    and (CLI.__STDIN_FILENAME == fp)):
                ffp = CLI.__STDIN_FILENAME
                self.__use_stdin = True
            else:
                ffp = self._validate_input_filepath(fp)
            self.__input_filepaths.append(ffp)
        # Validate the export target
        #
        self._validate_export_target(self.args.exportTarget)
        # Validate the remaining arguments
        #
        if self.args.leanPub:
            self.__book_txt_is_special = True
        if self.args.forceBook:
            self.__stdin_is_book = True
        if self.args.ignoreTransclusions:
            self.__ignore_transclusions = True
        if self.args.justRaw:
            self.__just_raw = True

    def _validate_export_target(self, export_target):
        """Validate the export target argument."""
        if export_target is not None:
            if 'html' == export_target:
                self.__wildcard_extension_is = ".html"
            elif 'latex' == export_target:
                self.__wildcard_extension_is = ".tex"
            elif 'lyx' == export_target:
                self.__wildcard_extension_is = ".lyx"
            elif 'opml' == export_target:
                self.__wildcard_extension_is = ".opml"
            elif 'rtf' == export_target:
                self.__wildcard_extension_is = ".rtf"
            elif 'odf' == export_target:
                self.__wildcard_extension_is = ".odf"
            else:
                raise ValueError(
                    "Unknown export target: {0}".format(export_target))

    def _validate_input_filepath(self, filepath):
        """Verify the input file path.

        Verify that if the file exists it is a regular file, or if the file
        doesn't exist that the parent directory does exist.

        Returns:
            The full absolute path of the validated file.

        Raises:
            parser.error: The file is not a regular file or it doesn't exist.

        """
        fnf = False
        try:
            if CLI.__STDIN_FILENAME == filepath:
                self.parser.error(
                    "You cannot specify both stdin ('-') and input files.")
            st = os.stat(filepath)
            mode = st.st_mode
            if stat.S_ISREG(mode):
                fullpath = os.path.abspath(filepath)
                return fullpath
            else:
                self.parser.error(
                    "'{0}' is not a regular file.".format(filepath))
        except OSError:
            fnf = True

        if fnf:
            self.parser.error(
                "'{0}' does not exist.".format(filepath))

    def _validate_output_filepath(self, filepath):
        """Verify the output file path.

        Verify that if the file exists it is a regular file, or if the file
        doesn't exist that the parent directory does exist.

        Returns:
            The full absolute path of the validated file.

        Raises:
            self.parser.error: The file is not a regular file
                or it doesn't exist.

        """
        try:
            st = os.stat(filepath)
            mode = st.st_mode
            if stat.S_ISREG(mode):
                fullpath = os.path.abspath(filepath)
                return fullpath
            else:
                fmts = "'{0}' is not a regular file and cannot be overwritten."
                self.parser.error(fmts.format(filepath))
        except OSError:
            pass

        fullpath = os.path.abspath(filepath)
        dirpath = os.path.dirname(fullpath)
        try:
            st = os.stat(dirpath)
            mode = st.st_mode
            if stat.S_ISDIR(mode):
                return fullpath
            else:
                fmts = "'{0}' is not a directory; invalid output file path"
                self.parser.error(fmts.format(dirpath))
        except OSError:
            fmts = (
                "The directory '{0}' does not exist;"
                " invalid output file path")
            self.parser.error(fmts.format(dirpath))

    def execute(self):
        """Merge the files."""
        if self.__abandon_cli:
            return

        if self.args.showVersion:
            self._show_version()
            return

        if self.__use_stdout:
            self.__out_file = self.__stdout
        else:
            self.__out_file = io.open(
                self.__out_filepath, 'w', encoding='utf-8')

        discard_metadata = False
        first_time = True
        merger = MarkdownMerge(
            wildcard_extension_is=self.__wildcard_extension_is,
            book_txt_is_special=self.__book_txt_is_special,
            stdin_is_book=self.__stdin_is_book,
            ignore_transclusions=self.__ignore_transclusions,
            just_raw=self.__just_raw)
        for ipath in self.__input_filepaths:
            infile_node = None
            if CLI.__STDIN_FILENAME == ipath:
                infile_node = Node(os.getcwd())
            else:
                infile_node = Node(file_path=os.path.abspath(ipath))
            if not first_time:
                # insert blank line between files
                self.__out_file.write("\n")
                # ignore metadata in subsequent files
                discard_metadata = True
            first_time = False
            merger.merge(infile_node, self.__out_file, discard_metadata)

        if not self.__use_stdout:
            self.__out_file.close()

    def parse_command_args(self, args):
        """Parse the command line arguments."""
        if self.__abandon_cli:
            return

        if (self.__stdout_redirected
                and self.__stderr_redirected):
            with CLI.RedirectStdStreams(
                    stdout=self.__stdout, stderr=self.__stderr):
                self.args = self.parser.parse_args(args)
                self._validate_args()
        else:
            self.args = self.parser.parse_args(args)
            self._validate_args()


# -------------------------------------------------------------------------+
# entry points for setuptools
# -------------------------------------------------------------------------+


def mdmerge_command():
    """Entry point for command installed by setuptools."""
    try:
        m = CLI()
        m.parse_command_args(sys.argv[1:])
        m.execute()
    except KeyboardInterrupt:
        print("")


# -------------------------------------------------------------------------+
# module's main method
# -------------------------------------------------------------------------+


if '__main__' == __name__:
    try:
        m = CLI()
        m.parse_command_args(sys.argv[1:])
        m.execute()
    except KeyboardInterrupt:
        print("")

# eof
