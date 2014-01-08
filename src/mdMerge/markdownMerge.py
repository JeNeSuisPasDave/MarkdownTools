# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import os
import os.path
import sys

"""TODO:

* Make use of Node to ensure no cycles
* Implement the show version option
* Parse lines for simple includsion: <<[filepath]
* Parse lines for fenced block inclusion: <<[highlight hint](code-filepath)
* Parse lines for simple inclusion, but after Markdown processing: <<{filepath}

"""

class CLI:


    class Node:
        """A tree node used to build a tree of filepaths that contain
        no cycles.

        """

        def __init__(self, filePath=None, parentNode=None):
            self.__filePath = filePath
            self.__parent = parentNode
            self.__children = []

        def IsAncestor(self, filePath):
            if self.__filePath == filePath:
                return true;
            if self.__parent.__filePath == None:
                return false;
            return self.__parent.IsAncestor(filePath)

        def AddChild(self, filePath):
            if self.IsAncestor(filePath):
                fmts = ("Circular reference."
                    " File '{0}' and an ancestor of itself.")
                raise AssertionError(fmts.format(filePath))
            node = Node(filePath, self)
            self.__children.append(node)
            return node

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
    __STDIN_FILENAME = '--'

    def __init__(self, stdin=None, stdout=None, stderr=None):
        """Constructor

        """

        import os.path
        import argparse

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
        self.__root = CLI.Node()
        self.__useStdout = True
        self.__outFilepath = None
        self.__outfile = None
        self.__inputFilepaths = []

        # main command
        #
        self.parser = argparse.ArgumentParser(
            description=("Concatenate and include multiple markdown"
            "files into a single file"), prog='mdmerge')
        self.parser.add_argument(
            '--version', dest='showVersion', action='store_true',
            default=False, help="show the software version")
        self.parser.add_argument(
            '-o', '--outfile', dest='outFile', action='store',
            help="Specify the path to the output file")
        self.parser.add_argument(
            dest='filepaths', metavar='filepath', nargs='*',
            help="A file to concatenate or '--' for stdin")

    def _ValidateInputFilepath(self, filepath):
        """Verify that if the file exists it is a regular file, or if the file
        doesn't exist that the parent directory does exist.

        Returns:
            The full absolute path of the validated file.

        Raises:
            IOError: The file is not a regular file or it doesn't exist.

        """

        import stat

        try:
            st = os.stat(filepath)
            mode = st.mode
            if stat.S_ISREG(mode):
                fullpath = os.path.abspath(filepath)
                return fullpath
            else:
                raise IOError(
                    "'{0}' is not a regular file.".format(filepath))
        except FileNotFoundError:
            raise IOError(
                "'{0}' does not exist.".format(filepath))

    def _ValidateOutputFilepath(self, filepath):
        """Verify that if the file exists it is a regular file, or if the file
        doesn't exist that the parent directory does exist.

        Returns:
            The full absolute path of the validated file.

        Raises:
            IOError: The file is not a regular file or it doesn't exist.
            
        """

        import stat

        try:
            st = os.stat(filepath)
            mode = st.mode
            if stat.S_ISREG(mode):
                fullpath = os.path.abspath(filepath)
                return fullpath
            else:
                fmts = "'{0}' is not a regular file and cannot be overwritten." 
                raise IOError(fmts.format(filepath))
        except FileNotFoundError:
            pass

        fullpath = os.path.abspath(filepath)
        dirpath = os.path.dirname(fullpath)
        try:
            st = os.stat(dirpath)
            mode = st.mode
            if stat.S_ISDIR(mode):
                return fullpath
            else:
                fmts = "'{0}' is not a directory; invalid output file path"
                raise IOError(fmts.format(dirpath))
        except FileNotFoundError:
            fmts = ("The directory '{0}' does not exist;"
                " invalid output file path")
            raise IOError(fmts.format(dirpath))

    def _ValidateArgs(self):
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
            self.__outFilepath = self._Validate(self.args.outFile)
        if 0 == len(self.args.filepaths):
            self.__useStdin = True
            self.__inputFilepaths.append(CLI.__STDIN_FILENAME)
        else:
            for fp in self.args.filepaths:
                ffp = None
                if CLI.__STDIN_FILENAME == fp:
                    ffp = CLI.__STDIN_FILENAME
                else:
                    ffp = self._ValidateInputFilepath(fp) 
                self.__inputFilepaths.append(ffp)

    def _ScanFile(self, ifile):
        """Store input lines into output file. If the input line is an
        include statement, then insert that files lines into the output
        file.

        """

        for line in ifile:
            if self.__useStdout:
                print(line, file=self.__outfile)
            else:
                print(line, file=self.__outfile)

    def _ShowVersion(self):
        """Show the version only.

        """

        import mdMerge

        print("mdmerge version {0}".format(mdMerge.__version__),
            file=self.__stdout)

    def _StdinIsTTY(self):
        """Detect whether the stdin is mapped to a terminal console.

        I found this technique in the answer by thg435 here:
        http://stackoverflow.com/questions/13442574/how-do-i-determine-if-sys-stdin-is-redirected-from-a-file-vs-piped-from-another

        """

        import os, stat

        mode = os.fstat(0).st_mode
        if ((not stat.S_ISFIFO(mode)) # piped
        and (not stat.S_ISREG(mode))): # redirected
            return True
        else: # not piped or redirected, so assume terminal input
            return False

    def Execute(self):
        """Merge the files.

        """

        if self.__abandonCLI:
            return

        if self.args.showVersion:
            self._ShowVersion()
            return

        if self.__useStdout:
            self.__outfile = self.__stdout
        else:
            self.__outfile = open(self.__outFilepath, 'w')

        for ipath in self.__inputFilepaths:
            if CLI.__STDIN_FILENAME == ipath:
                ifile = self.__stdin
                self._ScanFile(ifile)
            else:
                ifile = open(ipath, 'r')
                self._ScanFile(ifile)
                close(ifile)

    def ParseCommandArgs(self, args):
        """Parse the command line arguments.

        """

        if self.__abandonCLI:
            return

        if (self.__stdoutRedirected
        and self.__stderrRedirected):
            with CLI.RedirectStdStreams(
                stdout=self.__stdout, stderr=self.__stderr):
                self.args = self.parser.parse_args(args)
                self._ValidateArgs()
        else:
            self.args = self.parser.parse_args(args)
            self._ValidateArgs()


# -------------------------------------------------------------------------+
# module's main method
# -------------------------------------------------------------------------+

if '__main__' == __name__:
    try:
        m = CLI()
        m.ParseCommandArgs(sys.argv[1:])
        m.Execute()
    except KeyboardInterrupt:
        print("")
