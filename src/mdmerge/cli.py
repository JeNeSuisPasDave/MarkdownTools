# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from __future__ import print_function, with_statement, generators, \
    unicode_literals
import argparse
import os
import os.path
import stat
import sys

from .node import Node
from .markdownMerge import MarkdownMerge

class CLI:
    """Handle the command line interface, invoking MarkdownMerge as
    needed.

    """

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

    # class attributes
    #
    __STDIN_FILENAME = '-'

    def __init__(self, stdin=None, stdout=None, stderr=None):
        """Constructor

        """

        self.__stdinRedirected = False
        if stdin is not None:
            self.__stdin = stdin
            self.__stdinRedirected = True
        else:
            self.__stdin = sys.stdin
        self.__stdoutRedirected = False
        if stdout is not None:
            self.__stdout = stdout
            self.__stdoutRedirected = True
        else:
            self.__stdout = sys.stdout
        self.__stderrRedirected = False
        if stderr is not None:
            self.__stderr = stderr
            self.__stderrRedirected = True
        else:
            self.__stderr = sys.stderr

        self.__abandonCLI = False
        self.__useStdin = False
        self.__posStdin = 0
        self.__useStdout = True
        self.__outFilepath = None
        self.__outfile = None
        self.__inputFilepaths = []
        self.__bookTxtIsSpecial = False
        self.__wildcardExtensionIs = None
        self.__stdinIsBook = False

        # main command
        #
        self.parser = argparse.ArgumentParser(
            description=("Concatenate and include multiple markdown"
            "files into a single file"), prog='mdmerge')
        self.parser.add_argument(
            '--version', dest='showVersion', action='store_true',
            default=False, help="show the software version")
        self.parser.add_argument(
            "--export-target", dest='exportTarget', action='store',
            choices=['html','latex','lyx','opml','rtf','odf'],
            default='html',
            help="Guide include file wildcard substitution")
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
            help="One or more files to merge, or just '-' for STDIN")

    def _isSequenceNotString(self, obj):
        return (
            not hasattr(obj, "strip") and
            hasattr(obj, "__getitem__") or
            hasattr(obj, "__iter__"))

    def _isSequenceOfChars(self, obj):
        if not self._isSequenceNotString(obj):
            return False
        if (0 == len(obj)):
            return False
        for c in obj:
            if 1 != len(c):
                return False
        return True

    def _validateArgs(self):
        """Validate the command line arguments and set fields based on those
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
        if self.args.outFile != None:
            self.__useStdout = False
            self.__outFilepath = self._validateOutputFilepath(
                self.args.outFile)
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
        if 0 != len(self.args.inFiles):
            if self._isSequenceOfChars(self.args.inFiles):
                self.args.inFiles = [''.join(self.args.inFiles)]
        # Now validate the input file paths (or the '-' stdin designator)
        #
        for fp in self.args.inFiles:
            ffp = None
            if (1 == len(self.args.inFiles)
            and CLI.__STDIN_FILENAME == fp):
                ffp = CLI.__STDIN_FILENAME
                self.__useStdin = True
            else:
                ffp = self._validateInputFilepath(fp)
            self.__inputFilepaths.append(ffp)
        self._validateExportTarget(self.args.exportTarget)
        if self.args.leanPub:
            self.__bookTxtIsSpecial = True
        if self.args.forceBook:
            self.__stdinIsBook = True

    def _validateExportTarget(self, exportTarget):
        if exportTarget is not None:
            if 'html' ==  exportTarget:
                self.__wildcardExtensionIs = ".html"
            elif 'latex' ==  exportTarget:
                self.__wildcardExtensionIs = ".tex"
            elif 'lyx' ==  exportTarget:
                self.__wildcardExtensionIs = ".lyx"
            elif 'opml' ==  exportTarget:
                self.__wildcardExtensionIs = ".opml"
            elif 'rtf' ==  exportTarget:
                self.__wildcardExtensionIs = ".rtf"
            elif 'odf' ==  exportTarget:
                self.__wildcardExtensionIs = ".odf"
            else:
                raise ValueError(
                    "Unknown export target: {0}".format(exportTarget))

    def _validateInputFilepath(self, filepath):
        """Verify that if the file exists it is a regular file, or if the file
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

    def _validateOutputFilepath(self, filepath):
        """Verify that if the file exists it is a regular file, or if the file
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
            fmts = ("The directory '{0}' does not exist;"
                " invalid output file path")
            self.parser.error(fmts.format(dirpath))

    def _showVersion(self):
        """Show the version only.

        """

        import mdmerge

        print("mdmerge version {0}".format(mdmerge.__version__),
            file=self.__stdout)

    def _stdinIsTTY(self):
        """Detect whether the stdin is mapped to a terminal console.

        I found this technique in the answer by thg435 here:
        http://stackoverflow.com/questions/13442574/how-do-i-determine-if-sys-stdin-is-redirected-from-a-file-vs-piped-from-another

        """


        mode = os.fstat(0).st_mode
        if ((not stat.S_ISFIFO(mode)) # piped
        and (not stat.S_ISREG(mode))): # redirected
            return True
        else: # not piped or redirected, so assume terminal input
            return False

    def execute(self):
        """Merge the files.

        """

        if self.__abandonCLI:
            return

        if self.args.showVersion:
            self._showVersion()
            return

        if self.__useStdout:
            self.__outfile = self.__stdout
        else:
            self.__outfile = open(self.__outFilepath, 'w')

        merger = MarkdownMerge(
            wildcardExtensionIs=self.__wildcardExtensionIs,
            bookTxtIsSpecial=self.__bookTxtIsSpecial,
            stdinIsBook=self.__stdinIsBook)
        for ipath in self.__inputFilepaths:
            infileNode = None
            if CLI.__STDIN_FILENAME == ipath:
                infileNode = Node(os.getcwd())
            else:
                infileNode = Node(filePath=os.path.abspath(ipath))
            merger.merge(infileNode, self.__outfile)

        if not self.__useStdout:
            self.__outfile.close()

    def parseCommandArgs(self, args):
        """Parse the command line arguments.

        """

        if self.__abandonCLI:
            return

        if (self.__stdoutRedirected
        and self.__stderrRedirected):
            with CLI.RedirectStdStreams(
                stdout=self.__stdout, stderr=self.__stderr):
                self.args = self.parser.parse_args(args)
                self._validateArgs()
        else:
            self.args = self.parser.parse_args(args)
            self._validateArgs()


# -------------------------------------------------------------------------+
# module's main method
# -------------------------------------------------------------------------+

if '__main__' == __name__:
    try:
        m = CLI()
        m.parseCommandArgs(sys.argv[1:])
        m.execute()
    except KeyboardInterrupt:
        print("")

# eof