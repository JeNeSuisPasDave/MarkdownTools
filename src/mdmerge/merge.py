# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import os
import os.path
import sys
import argparse
import re
import io

class MarkdownMerge:

    def __init__(self, wildcardExtensionIs):
        self.__wildcardExtensionIs = wildcardExtensionIs

        self.__reoLeanpubIndexMarker = re.compile("^frontmatter\:$")
        self.__reoMultiMarkdownIndexMarker = re.compile("^#merge$")
        self.__reoMmdTransclusion = re.compile("^\{\{(.+)\}\}$")
        self.__reoPathAndWildcardExtension = re.compile("^(.+)\.\*$")
        self.__reoMarkedInclude = re.compile("^<<\[(.+)\]$")
        self.__reoLeanpubInclude = re.compile("^<<\((.+)\)$")
        self.__reoLeanpubCodeInclude = re.compile("^<<\[.*\]\((.+)\)$")

    def _findIncludePath(self, lines):
        """Detect wheter line is an include specification.

        Args:
            lines: up to 5 lines of input to be examined for file
                include specifications
        Returns:
            None if the line is not an include specification. Otherwise,
            returns the file specification as a string value.

        """

        if None == lines:
            return None

        # look for code file transclusion specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A code fence start (e.g. `~~~` or `~~~python` or similar, followed by
        #   3. A line containing only `{{filepath}}`, followed by
        #   4. A code fence termination (e.g. `~~~`), followed by
        #   5. Another blank line.
        #
        # Of course, the first line could be None, indicating top of file.
        # And the last line could be None, indicating end of file
        #
        if (5 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[4])
            and self._lineIsCodeFence(lines[1])
            and self._lineIsEndingFence(lines[3])):
                spec = self._findTransclusion(lines[2])
                if (None != spec):
                    return spec

        # look for normal file transclusion specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `{{filepath}}`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[2])):
                spec = self._findTransclusion(lines[1])
                if (None != spec):
                    return spec

        # look for Marked file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<[filepath]`, followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[2])):
                spec = self._findMarkedInclude(lines[1])
                if (None != spec):
                    return spec

        # look for Leanpub file include specification, which is:
        #
        #   1. A blank line, followed by
        #   2. A line containing only `<<(filepath)`, or
        #      `<<[code caption](filepath) followed by
        #   3. Another blank line.
        #
        if (3 == len(lines)):
            if (self._stringIsNullOrWhitespace(lines[0])
            and self._stringIsNullOrWhitespace(lines[2])):
                spec = self._findLeanpubInclude(lines[1])
                if (None != spec):
                    return spec

        # Get out
        #
        return None

    def _findLeanpubInclude(self, line):
        """Parse the line looking for a Leanpub file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """

        m = self.__reoLeanpubInclude.match(line)
        if not m:
            m = self.__reoLeanpubCodeInclude.match(line)
            if not m:
                return None
        filepath = m.group(1)
        return filepath

    def _findMarkedInclude(self, line):
        """Parse the line looking for a Marked file include
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file include specification is found in the line.
            If a file include specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """

        m = self.__reoMarkedInclude.match(line)
        if not m:
            return None
        filepath = m.group(1)
        return filepath

    def _findTransclusion(self, line):
        """Parse the line looking for a Multimarkdown file transclusion
        specification.

        Args:
            line: The line of the input file to examine.

        Returns:
            `None` if no file transclusion specification is found in the line.
            If a file transclusion specification is found in the line, then
            the specified file path is returned. If the specified path used
            a wildcard extension, the the wildcard is replaced with the
            export extension.

        """

        m = self.__reoMmdTransclusion.match(line)
        if not m:
            return None
        filepath = m.group(1)
        if filepath.endswith(".*"):
            m = self.__reoPathAndWildcardExtension.match(filepath)
            if m:
                filepath = "{0}{1}".format(
                    m.group(1), self.__wildcardExtensionIs)
        return filepath

    def _isLeanpubIndexMarker(self, line):
        """Detect whether line is 'frontmatter:', indicating the line
        is a marker for leanpub index files.

        Returns:
            True if the line is 'frontmatter:'; otherwise, False.

        """

        m = self.__reoLeanpubIndexMarker.match(line)
        if not m:
            return False;
        return True;

    def _isMultiMarkdownIndexMarker(self, line):
        """Detect whether line is '#merge', indicating the line
        is a marker for mmd_merge index files.

        Returns:
            True if the line is '#merge'; otherwise, False.

        """

        m = self.__reoMultiMarkdownIndexMarker.match(line)
        if not m:
            return False;
        return True;

    def _mergedLines(self, inFileNode, inFile):
        """A generator function that examines each line of the
        input file and recursively calls itself for each included
        file.

        Args:
            inFileNode: the Node object representing the input file
            inFile: the file object of the opened input file

        Returns:
            The next line to be written to the output file, or None
            if there are no more input lines.

        """

        from collections import deque

        buf5 = deque(maxlen=5)
        buf3 = deque(maxlen=3)
        buf5.append(None) # indicate top of file
        buf3.append(None) # indicate top of file

        while True:
            mLine = None
            line = inFile.readline()
            if not line:
                if (0 == len(buf5)):
                    break
                else:
                    mLine = buf5.popleft()
                    if not mLine:
                        break
                    yield mLine
            else:
                mLine = buf5.popleft()
                buf5.append(line)
                buf3.append(line)
                includePath = self._findIncludePath(buf5)
                if includePath:
                    # consuming the fenced code with include;
                    # clear all but the final blank line
                    for x in range(4):
                        buf5.popleft()
                    for x in range(2):
                        buf3.popleft()
                else:
                    includePath = self._findIncludePath(buf3)
                    if includePath:
                        # consuming the include;
                        # clear to the final blank line
                        for x in range(2):
                            buf5.popleft()
                            buf3.popleft()
                if includePath:
                    # merge in the include file
                    #
                    includedInFileNode = inFileNode.addChild(includePath)
                    includedInFile = open(includePath, "r")
                    for deeperLine in self._mergedLines(
                        includedInFileNode, includedInFile):
                        yield deeperLine
                yield mLine

    def _stringIsNullOrWhitespace(self, s):
        """Detect whether the string is null, empty, or contains only
        whitespace.

        Args:
            s: the string object to test

        Returns:
            True if the string is None, zero-length, or contains only
            whitespace characters. Otherwise returns False.

        """

        if None == s:
            return True
        if 0 == len(s):
            return True
        if s.isspace():
            return True
        return False

    def merge(self, inFileNode, outFile):
        inFilePath = inFileNode.filePath()
        with io.open(inFilePath, "r") as inFile:
            for line in self._mergedLines(inFileNode, inFile):
                outLine = line.rstrip(['\r','\n'])
                outFile.write(outLine + '\n')

    def merge2(self, inFileNode, inFile, outFile):
        """Read every line of inFile and write to outFile. If inFile
        line is an include statement, then read the specified file
        into the outFile by calling Merge() recursively.

        """

        isFirstLine = True
        fileIsLeanpubIndex = False
        fileIsMultimarkdownIndex = False
        for line in inFile:
            if isFirstLine:
                isFirstLine = False
                if (self._isLeanpubIndexMarker(line)):
                    fileIsLeanpubIndex = True
                    continue
                if (self._isMultiMarkdownIndexMarker(line)):
                    fileIsMultimarkdownIndex = True
                    continue
            mergeFilePath = _findMergeInclude(line)
            if mergeFilePath is not None:
                nextFilePath = self._getFullPath(mergeFilePath)
                nextFile = open(nextFilePath, 'r')
                nextFileNode = inFileNode.AddNode(nextFilePath)
                self.Merge(nextFileNode, nextFile, outFile)
                nextFile.close()
            else:
                print(line, file=self.__outfile, end='')

